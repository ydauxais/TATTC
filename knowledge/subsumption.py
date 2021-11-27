import logging
import sys
import os
import io
import pickle
import argparse

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import binarize
import scipy.sparse as sp


class Subsumption:
    def __init__(self, data, topics) -> None:
        self.data_path = data
        self.topics_path = topics
        self.is_topic_path = True
        self.topics_label = ""
        self.overlaps = None
        self.weights = None
        self.features = None
        self.ifeatures = None
        self.lengths = None

    def load_data(self):
        if os.path.exists(self.data_path):
            logging.info('loading preprocessed data from %s' % self.data_path)
            if self.data_path.endswith(".txt"):
                self.data = open(self.data_path, "r")
            else:
                with open(self.data_path, 'rb') as fin:
                    self.data = pickle.load(fin)
        else:
            logging.error("preprocessed data doesn't exist")
            sys.exit()

    def load_topics(self):
        fname = self.topics_path
        if not os.path.exists(fname):
            self.is_topic_path = False
            fname = '/calcul/datasets/nasa/topics-%s.txt' % self.topics_path
            if not os.path.exists(fname):
                logging.error("not a filename or a valid topic name")
                sys.exit()
        logging.info('loading topics from %s' % fname)
        with open(fname, 'r') as f_in:
            self.topics = f_in.read()
        self.topics = self.topics.split('\n')
        logging.info('loaded %d topics' % len(self.topics))

    def make_counts(self):
        logging.info("getting topics counts")
        pattern = "(?u)\\b[\\w-]+\\b"

        self.vectorizer = CountVectorizer(vocabulary=set(
            self.topics), token_pattern=pattern, ngram_range=(1, 3))
        self.counts = self.vectorizer.transform(self.data)
        if isinstance(self.data, io.IOBase):
            self.data.close()
        del(self.data)
        self.features = self.vectorizer.get_feature_names()
        self.ifeatures = {k: v for v, k in enumerate(self.features)}

    def make_matrices(self):
        logging.info("getting the overlap and weight matrices")
        self.counts = binarize(self.counts)
        self.overlaps = self.counts.T.dot(self.counts)
        # del(self.counts)
        self.overlaps.data *= self.overlaps.data > 1
        self.overlaps.eliminate_zeros()
        self.lengths = self.overlaps.diagonal()
        diagonal = sp.diags([1./x if x > 0 else 0 for x in self.lengths])
        self.overlaps = diagonal.dot(self.overlaps)

        self.weights = self.overlaps.minimum(self.overlaps.T)
        dotp_sub = self.overlaps - self.weights
        dotp_sub.eliminate_zeros()
        dotp_sub.data[dotp_sub.data > 0] = 1
        self.weights = self.weights.minimum(dotp_sub)
        self.weights.data *= -1

    def dump(self, obj, prefix, suffix):
        filename = prefix + "/" + \
            self.data_path.split("/")[-1].split(".")[0]
        if self.is_topic_path:
            if self.topics_label:
                filename += "-" + self.topics_label
        else:
            filename += "-" + self.topics_path 
        filename += suffix
        with open(filename, "wb") as fout:
            pickle.dump(obj, fout)


def main():
    parser = argparse.ArgumentParser(
        description='Compute the matrices relative to the subsumptions')
    parser.add_argument("--data", dest="data", type=str,
                        help="file containing the paper data")
    parser.add_argument("--topics", dest="topics", type=str,
                        help="filename or type of topic to use")
    parser.add_argument("--topics_label", dest="topics_label", type=str, default="",
                        help="label used for the topics in the output filename (optional)")
    parser.add_argument("--out", dest="out", type=str,
                        help="output file prefix")

    args = parser.parse_args()

    T = Subsumption(args.data, args.topics)
    T.topics_label = args.topics_label
    T.load_data()
    T.load_topics()

    T.make_counts()

    T.dump(T.vectorizer, args.out, "_vectorizer.pickle")
    del(T.vectorizer)
    # T.dump(T.counts, args.out, "_counts.pickle")

    T.make_matrices()
    T.dump(T, args.out, "_subsumption.pickle")


if __name__ == "__main__":
    main()
