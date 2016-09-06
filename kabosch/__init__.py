""" ka-bosch luigi pipeline activity
"""
import os
import getpass
import datetime
import logging
import requests
import bs4
import luigi
import luigi.util

# grab the luigi interface logger
LOGGER = logging.getLogger('luigi-interface')

# check for a plain text password file
if os.path.exists('.kaggle'):
    with open('.kaggle') as pwdfile:
        USERNAME, PASSWORD = pwdfile.read().split()
elif 'KAGGLE_PWD' in os.environ:
    USERNAME = os.environ['KAGGLE_UID']
    PASSWORD = os.environ['KAGGLE_PWD']
else:
    USERNAME = input('Kaggle username: ')
    PASSWORD = getpass.getpass('Kaggle password: ')


class Path(luigi.Config):  # pylint: disable=too-few-public-methods
    r""" Path: environment control to allow multiple pipeline runs

    The two valid values for the environment (ENV) are:
    * train
    * test
    """
    ENV = luigi.Parameter(default='train')
    RUNTAG = luigi.Parameter(default=datetime.datetime.now().date().isoformat())

    def resolve(self, directory, raw=False):
        assert self.ENV in ['train', 'test'], 'unknown environment'
        base_path = "{}{}{}".format('data', os.path.sep, self.ENV)  # data/train
        if raw:
            full_path = os.path.sep.join([base_path, directory])
        else:
            full_path = os.path.sep.join([base_path, self.RUNTAG, directory])
        LOGGER.info('resolving local path %s', full_path)
        return full_path


class KaggleTarget(luigi.Target):
    login_url = 'https://www.kaggle.com/account/login'

    def login(self):
        if hasattr(self, '_session'):
            return True
        else:
            self._session = requests.Session()
            resp = self._session.get(self.login_url)
            soup = bs4.BeautifulSoup(resp.text, 'html.parser')
            login_inputs = soup.find('form').find_all('input')
            login_dict = {ip.get('name'): ip.get('value') for ip in login_inputs if ip.get('name')}
            login_dict['UserName'] = USERNAME
            login_dict['Password'] = PASSWORD
            login_resp = self._session.post(self.login_url, data=login_dict)

            if self.login_url == login_resp.url:
                raise RuntimeError

            return True

    def get_resource(self, resource, stream=True):
        assert self.login() is True, 'unable to log in to Kaggle'
        target_url = 'https://www.kaggle.com{}'.format(resource)
        return self._session.get(target_url, stream=stream)

    def exists(self):
        return self.login()


@luigi.util.delegates
class Fetch(luigi.Task):
    r""" Fetch: download data from kaggle into a local environment
    """
    root = '/c/bosch-production-line-performance/download/{}'

    def subtasks(self):
        return [Path()]

    def run(self):
        kag = self.requires()[0].output()[0]
        with self.output()[0].open('w') as handle:
            datastream = kag.get_resource(self.root.format(self.resource))
            for chunk in datastream.iter_lines(chunk_size=1026):
                _ = handle.write(chunk)
                handle.flush()
