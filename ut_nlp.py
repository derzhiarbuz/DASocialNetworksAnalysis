# Created by Gubanov Alexander (aka Derzhiarbuz) at 17.10.2019
# Contacts: derzhiarbuz@gmail.com

import da_nlpbase
import pickle
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt

# file = open("D:/BigData/Guber/httpsvkcomriatomskcsv.pkl", "rb")
# tokenized_posts = pickle.load(file)
# file.close()
#bows = da_nlpbase.bag_of_words_dict(tokenized_posts)
#bou = da_nlpbase.bag_of_usage(bows)
# bow = da_nlpbase.bag_of_words_sets(tokenized_posts)
# dists, ord_dict = da_nlpbase.condensed_sets_similarity(bow)
# testdict = {1:{1,2,3,4}, 2:{1,2,3,4}, 3:{3,4,5,6}, 4:{1,2}}
# dists = da_nlpbase.condensed_sets_similarity(testdict)
# for d in dists:
#     print(d)
# print(dists)
# Z = linkage(dists, 'ward')
# print('linkage completed')
# print(ord_dict)

import io
import re

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage


def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        return text

import PyPDF4

if __name__ == '__main__':
    # pl = open('C:/Users/Al Gu/Downloads/1998Kraut-InternetParadox_1.pdf', 'rb')
    # plread = PyPDF4.PdfFileReader(pl)
    # print(plread.numPages)
    # for i in range(plread.numPages):
    #     getpage = plread.getPage(i+1)
    #     text = getpage.extractText()
    #     print(text)
    txt1 = extract_text_from_pdf('C:/Users/Al Gu/Downloads/1998Kraut-InternetParadox_1.pdf')
    txt2 = extract_text_from_pdf('C:/Users/Al Gu/Downloads/Beyond_Student_Perceptions_Issues_of_Interaction_P.pdf')

    rgxp = r'(\d+\. .+? [12][890]\d\d\)?\.)'
    occurs1 = re.findall(rgxp, txt1)
    occurs2 = re.findall(rgxp, txt2)

    print(len(occurs1))
    for o in occurs1:
        print(o)
    print(len(occurs2))
    for o in occurs2:
        print(o)





