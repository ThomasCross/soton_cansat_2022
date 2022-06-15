import logging

from datetime import datetime


def setup_logging(filename, path='//cansat//'):
    file = filename + ("-{}.log".format(datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")))

    logging.basicConfig(
        encoding='utf-8',
        filename=path + file,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logging.info('Logger Started')
