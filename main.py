import aspell
from pyMorfologik import Morfologik
from pyMorfologik.parsing import ListParser
import json
from deletions import get_deletions_from_file
from sklearn.feature_extraction.text import  TfidfVectorizer
import numpy as np
import os

# usuwanie słów przystankowych
words_to_delete = get_deletions_from_file()

all_files = {
    "grozby_karalne": [],
    "obrazliwe": [],
    "dopuszczalne": [],
    "zlosliwe": [],
    "krytyka": [],
    "ostra_krytyka": []
}


def get_json_content(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)


def replace_all_characters(comment, characters):
    for c in characters:
        comment = comment.replace(c, " ")

#oczyszczanie komentarzy
def get_cleared_comment(com):
    result = []
    comment = com.replace(",", " ").replace(".", " ").replace("-", " ").replace("!", " ").replace("?", " ").replace(":", " ").replace("@", "").replace(";", " ").replace("(", "").replace(")", "")
    comment = [x.lower() for x in comment.split(" ") if x != ""]
    output = stemmer.stem(comment, parser)
    for word in output:
        possible = list(word[1].keys())
        if len(possible) > 0:
            if possible[0] not in words_to_delete:
                result.append(possible[0])
        else:
            suggestion = speller.suggest(word[0])
            if len(suggestion) != 0:
                if suggestion[0] not in words_to_delete:
                    result.append(suggestion[0])
            else:
                result.append(word[0])
                print(word[0], " nierozpoznane!")
    return result


def get_json_files_as_list(filepath):
    json_files = sorted(
        [file for file in os.listdir("rodzaje_komentarzy/{}".format(filepath)) if file.endswith(".json")],
        key=lambda x: int(x.split(".")[0])
    )
    all_files[filepath].extend(json_files)


# Morfologik to narzędzie do lematyzacji i oznaczania częsci mowy
# Aspell to korektor pisowni
rws = "/Users/adrianamackow/PycharmProjects/cross_validation/aspell6-pl-6.0_20191103-0/pl.rws"
speller = aspell.Speller(('lang', 'pl'), ('master', rws))
parser = ListParser()
stemmer = Morfologik()

get_json_files_as_list("grozby_karalne")
get_json_files_as_list("obrazliwe")
get_json_files_as_list("dopuszczalne")

get_json_files_as_list("krytyka")
get_json_files_as_list("ostra_krytyka")
get_json_files_as_list("zlosliwe")


all_comments = []

VECTOR_for_all = [0]*len(all_files["dopuszczalne"]) + \
                 [1]*len(all_files["ostra_krytyka"]) + [1]*len(all_files["krytyka"]) + \
                 [2] * len(all_files["grozby_karalne"]) + [2] * len(all_files["obrazliwe"]) + [2] * len(all_files["zlosliwe"])
new_VECTOR_for_all = []

for v in VECTOR_for_all:
    if v == 0:
        new_VECTOR_for_all.append([1, 0, 0])
    if v == 1:
        new_VECTOR_for_all.append([0, 1, 0])
    if v == 2:
        new_VECTOR_for_all.append([0, 0, 1])
print(len(new_VECTOR_for_all))

all_length = len(new_VECTOR_for_all)
print(new_VECTOR_for_all)


with open("target_file_3class2", 'w') as f:
    f.writelines(str(new_VECTOR_for_all))

count = 0

for dir in all_files.keys():
    for file in all_files[dir]:
        count += 1
        print("{}/{}".format(count, all_length))
        try:
            content = get_json_content("rodzaje_komentarzy/{}/{}".format(dir, file))
            cleared = get_cleared_comment(content["komentarz"])
            all_comments.append(cleared)
        except Exception as e:
            print(e)
            all_comments.append("")

feature_for_all = np.array([" ".join(x) for x in all_comments])

#Kodowanie tekstu za pomoca określenia wagi słow
tfidf = TfidfVectorizer(sublinear_tf=True, use_idf=True)
feature_matrix = tfidf.fit_transform(feature_for_all)
np.save('data_tfidf.npy', feature_matrix.toarray())


# Kodowanie slów za pomocą worka slów
count_vec = CountVectorizer()
bag_of_words = count_vec.fit_transform((feature_for_all))
np.save('data_3class_bag_of_words.npy', bag_of_words.toarray())
