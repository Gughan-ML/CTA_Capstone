
"""
READ ME:

1) Please make sure to have all the required packages installed before running the script.
2) This script takes two CSV files to match JDs.
    - final.csv : the output file produced from the ONET crawling API
    - CTA final.csv : the output file provided by the CTA HR team 3.
                      It contains all the CTA JDs in a CSV file format.
3) The final output will be saved in a file, "top5_matches.csv".

The tfidf model assumes that words that occur relatively rarely have more differential power;
if "knowledge" occurs across all documents, then "knowledge" does not differentiate the document A from the doc B.
So, the tfidf model weighs relatively rare words more than ones that frequently appear in documents.

NOTE:
For future use, once the database from the team 1 is up and verified, the part where this script
reads in the CTA JD to feed the model should be changed to read data directly from the database.
This script is not connected to the database because our understanding is that the database is
yet to be verified.
"""


# Required packages
import pandas as pd #for reading and manipulating in files
import numpy as np #for manipulating data
import re #for cleaning the documents
from nltk.stem import WordNetLemmatizer #for trnasforming words for better similarity scores
from nltk.corpus import stopwords #for removing words like "an", "the", "it"
from nltk.tokenize import word_tokenize #for spliting documents into words
from sklearn.feature_extraction.text import TfidfVectorizer #for modeling
from sklearn.metrics.pairwise import cosine_similarity #for matching
import os
import errno

### Download nltk resources
import nltk
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")
#more data cleaning

lemmatizer = WordNetLemmatizer() #importing lemmatizer
STOPWORDS = list(stopwords.words("english")) #importing stopwords

#function to clean data more
def cleaning(string):
    temp = word_tokenize(string.lower()) #break the document into words
    lemma = [lemmatizer.lemmatize(i, "v") for i in temp] #lemmatize
    stop = [i for i in lemma if i not in STOPWORDS] #remove articles, pronouns, and etc
    stop = [re.sub(r"[^a-z0-9]", "", i) for i in stop] #remove anything that is not a word
    stop2 = [i for i in stop if re.search(r"[a-z-]{3,}", i)] #get words with 3 or more letters
    stop2 = [i for i in stop2 if i != "nan" ] #get rid of null values
    return stop2


''' Main function to run the modelling'''
def main():
    input_path = os.path.join(os.getcwd(),"input/")
    input_file = os.listdir(input_path)
    #importing cta data

    if len(input_file)==0:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
        sys.exit(0)

    cta = pd.read_csv(input_path + input_file[0], sep="#")
    cta.drop("CHALLENGES", axis = 1, inplace=True) #dropping the challenge section

    #importing ONET JDs
    onet_path = os.path.join(os.path.dirname(os.getcwd()),"ONET SCRAPPING API/output/csv/")
    onet_filename = os.listdir(onet_path)

    onet = pd.read_csv(onet_path + onet_filename[0], sep=",")
    moc = pd.DataFrame({"title":onet["Code"].str.cat(onet["Title"], sep = " ").tolist(),
                        "moc":onet["MOCs"]
                       })
    onet.drop(["Job Zone", "MOCs", "Military_Branch"], axis = 1, inplace = True)

    #data cleaning started
    #joining all columns into one string
    cta["new"] = pd.Series(cta.astype(str).values.tolist()).str.join("  ")
    onet["new"] = pd.Series(onet.astype(str).values.tolist()).str.join("  ")

    #data cleaning
    cta["new"] = cta["new"].apply(lambda x: str(x).replace("#", ", ").replace(".", ". "))
    onet["new"] = onet["new"].apply(lambda x: str(x).replace("#", ", ").replace(".", ". "))

    #deleting the title only JDs
    all_other = []
    for ind, i in enumerate(onet["Title"].tolist()):
        lowercase = i.lower()
        if "all other" in lowercase:
            all_other.append(ind)
    onet = onet.drop(onet.index[all_other])

    #taking some time about 5 min. Cleaning the data
    cta["clean"] = cta["new"].apply(cleaning)
    onet["clean"] = onet["new"].apply(cleaning)

    #making columns for the cosine similarity dataframe
    onet_columns = onet["Code"].str.cat(onet["Title"], sep = " ").tolist()
    cta_columns = cta["JSN"].astype(str).str.cat(cta["title"], sep = " ").tolist()

    all_columns = ["CTA "+i for i in cta_columns] + ["ONET "+i for i in onet_columns]
    cta_onet = [" ".join(i) for i in cta["clean"]]+[" ".join(i) for i in onet["clean"]] #get the documents

    #Create the Document Term Matrix
    #taking tfidf to weigh the words and then run cosine similarity.
    tfidf_vectorizer = TfidfVectorizer() #import the weighing algo
    sparse_matrix = tfidf_vectorizer.fit_transform(cta_onet) #weigh the words and the result is a matrix

    doc_matrix = sparse_matrix.todense() #make the matrix more concise
    df = pd.DataFrame(doc_matrix, columns = tfidf_vectorizer.get_feature_names()) #make it into a dataframe

    tfidf_cosine =  cosine_similarity(df, df) #compare one document to another to get similiarity score
    tfidf_cosine_df = pd.DataFrame(tfidf_cosine,
                                   columns = all_columns,
                                   index = all_columns) #save the result as a dataframe

    #cut the dataframe so it contains cta*onet data
    cta_jds_num = cta.shape[0]
    tfidf_cosine_df2 = tfidf_cosine_df.iloc[0:cta_jds_num, cta_jds_num:]

    #putting 5 top matches for each CTA job
    all_val = []
    for ind in range(tfidf_cosine_df2.shape[0]):
        ary = tfidf_cosine_df2.iloc[ind, :] #take one CTA job at a time
        rs = ary.iloc[np.lexsort([ary.index, ary.values])][-5:][::-1] #sort matches in descending order and get top 5
        rs_index = rs.index #getting index/ONET job titles of the mathces
        rs_values = rs.values #getting the similiarity scores
        temp = list(zip(*(rs_index, rs_values))) #put job titles and scores together
        all_val.append([tfidf_cosine_df2.index[ind], temp]) #and then save the ONET job title-score pair with the CTA job

    all_tfidf_df = pd.DataFrame({"onet1": [i[1][0][0] for i in all_val],
                                  "onet1_score": [i[1][0][1] for i in all_val],
                                  "onet2": [i[1][1][0] for i in all_val],
                                  "onet2_score": [i[1][1][1] for i in all_val],
                                  "onet3": [i[1][2][0] for i in all_val],
                                  "onet3_score": [i[1][2][1] for i in all_val],
                                  "onet4": [i[1][3][0] for i in all_val],
                                  "onet4_score": [i[1][3][1] for i in all_val],
                                  "onet5": [i[1][4][0] for i in all_val],
                                  "onet5_score": [i[1][4][1] for i in all_val]},
                                index = tfidf_cosine_df2.index)

    #find military codes for each match- getting ready
    moc = moc.fillna("NONE") #some job titles do not have the mocs
    moc_list = ["ONET "+title for title in moc["title"].tolist()] #taking the titles
    moc_col = [i+"_moc" for i in all_tfidf_df.columns.tolist()[::2]] #get the column names
    for col in moc_col:
        all_tfidf_df[col] = ["NONE" for i in range(all_tfidf_df.shape[0])] #making columns to the output df

    #find mocs for each job title
    for ind in range(all_tfidf_df.shape[0]):
        ary = all_tfidf_df.iloc[ind, :].tolist()[::2][0:5]
        for idx, i in enumerate(ary):
            place = moc_list.index(i)
            all_tfidf_df.iloc[ind, 10+idx] = ",".join(moc["moc"][place].split("#"))

    #Save the output
    all_tfidf_df.to_csv(os.path.join(os.getcwd(),"output/")+"top5_matches.csv")

if __name__=="__main__":main()
