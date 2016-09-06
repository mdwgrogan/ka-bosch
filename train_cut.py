""" Download and process training data.

The Bosch Kaggle competition comes with some large data sets in zip files. We
can use a python/luigi pipeline to help us manage analysis in a repeatable way.
"""
import os
import logging
import datetime
import luigi
import luigi.util
import kabosch
LOGGER = logging.getLogger('luigi-interface')


class KaggleReady(luigi.Task):

    def requires(self):
        return []

    def output(self):
        return [kabosch.KaggleTarget()]


class CategoricalData(kabosch.Fetch):

    @property
    def resource(self):
        resource_name = '{}_categorical.csv.zip'.format(self.subtasks()[0].ENV)
        return resource_name

    def requires(self):
        return [KaggleReady()]

    def output(self):
        file_placement = self.subtasks()[0].resolve(self.resource, raw=True)
        return [luigi.LocalTarget(file_placement, format=luigi.format.MixedUnicodeBytes)]


class DateData(kabosch.Fetch):

    @property
    def resource(self):
        resource_name = '{}_date.csv.zip'.format(self.subtasks()[0].ENV)
        return resource_name

    def requires(self):
        return [KaggleReady()]

    def output(self):
        file_placement = self.subtasks()[0].resolve(self.resource, raw=True)
        return [luigi.LocalTarget(file_placement, format=luigi.format.MixedUnicodeBytes)]


class NumericData(kabosch.Fetch):

    @property
    def resource(self):
        resource_name = '{}_numeric.csv.zip'.format(self.subtasks()[0].ENV)
        return resource_name

    def requires(self):
        return [KaggleReady()]

    def output(self):
        file_placement = self.subtasks()[0].resolve(self.resource, raw=True)
        return [luigi.LocalTarget(file_placement, format=luigi.format.MixedUnicodeBytes)]


class DownloadData(luigi.WrapperTask):  # pylint: disable=too-few-public-methods
    def requires(self):  # pylint: disable=no-self-use
        return [CategoricalData(),
                DateData(),
                NumericData()]


if __name__ == '__main__':
    luigi.run()
