#importing the libraries
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen, urlretrieve
import re, json, os, string
import urllib
from urllib.error import URLError, HTTPError
from socket import timeout
from collections import OrderedDict
import pandas as pd


def save_data(data):
    directory = os.getcwd()
    files = os.listdir(directory)
    files = [i.replace(".json", "") for i in files if ".json" in files]
    title = data["title"].replace("/", "")
    if title in files:
        pass
    else:
        with open(os.path.join(directory, title+".json"), "w") as file:
            json.dump(data, file)
            print(title+" is saved")


#for scraping sections in table form with 2 columns

table2columns = ["Knowledge", "Skills", "Abilities",
                 "WorkActivities", "Education", "Interests",
                 "WorkStyles", "WorkValues"
                ]

def makingTables(element, content_area):
    area = content_area.find("div", {"id":"wrapper_"+element})
    if area != None:
        element_list = []
        ths = area.findAll("th")
        rows = area.findAll("tr")
        for row in rows[1:]:
            tds = row.findAll("td")
            x = {ths[0].get_text(): tds[0].get_text().replace("\xa0", ""),
                 ths[1].get_text(): tds[1].get_text().split(" — ")[0].replace("\xa0", ""),
                 "description" : tds[1].get_text().split("— ")[-1].replace("\n", "")
                }
            element_list.append(x)
        return(element_list)
    else:
        pass


# In[137]:


#for sections in list forms with "-" joining the element and description

list2columns = ["TechnologySkills", "ToolsUsed"]

def makinglist(element, content_area):
    area = content_area.find("div", {"id":"wrapper_"+element})
    if area != None:
        element_list = []
        lis = area.findAll("li")
        for item in lis:
            sk = item.find("b").get_text()
            string = re.sub(r"\((.*?)\)", "", item.get_text())
            string = string.replace(sk, "").replace("—", "").replace("\n", "")
            string = string.split(";")
            string = [i.strip(" ") for i in string]
            x = {element: sk,
                  "details": string}
            element_list.append(x)
        return(element_list)
    else:
        pass


# In[145]:


#wrapper functions to catch errors and retry scraping each JD
def scrape_page_wrapper(page):
    counter = 0
    tries = 5
    while counter < tries:
        try:
            scrape_page(page)
            break
        except (URLError,
                HTTPError,
                timeout
               ) as e:
            print("****** ERROR on ", page)
            print("******* RETRY #", str(tries))
            tries -= 1


# In[155]:


#scraping each JD
def scrape_page(page):
    page = page.replace("summary", "details")
    print(page)
    req = urllib.request.Request(page, headers={ 'User-Agent': 'Mozilla/5.0' })
    html = urllib.request.urlopen(req).read()
    soup=BeautifulSoup(html, 'html.parser')

    #opening the job page
    data = OrderedDict()
    #job title
    title = soup.find("span", {"class":"titleb"}).get_text()

    files = os.listdir(os.getcwd())
    files = [i.replace(".json", "") for i in files if i.endswith(".json")]
    if title not in files:
        pass
    else:
        return None

    content_area = soup.find("div", {"id":"content"})

    #tasks
    tasks = []
    tasks_area = soup.select("div.section_Tasks > div > table > tr")
    if len(tasks_area) > 0:
        for row in tasks_area[1:]:
            tds = row.findAll("td")
            x = {"task": tds[2].get_text().replace("\n", ""),
                 "category": tds[1].get_text(),
                 "importance": tds[0].get_text()}
            tasks.append(x)
    else:
        return None

    #work context
    context = []
    context_area = soup.select("div.section_WorkContext > div > table > tr")
    if len(context_area) > 0:
        context_headers = context_area[0].findAll("th")
        context_headers = [i.get_text() for i in context_headers]
        for row in context_area[1:]:
            tds = row.findAll("td")
            subtable = tds[1].find("table")
            breakdown = []
            if subtable != None:
                subtable_rows = subtable.findAll("tr")
                for r in subtable_rows[1:]:
                    sub_tds = r.findAll("td")
                    percentage = sub_tds[0].find("b").get_text()
                    percentage_detail = sub_tds[1].get_text()
                    breakdown.append({"percentage":percentage+"%",
                                  "details":percentage_detail.replace("\xa0", "")})
            else:
                pass

            x = {context_headers[0]: tds[0].find("b").get_text(),
                         "description": tds[0].get_text().split("— ")[-1].replace("\n", ""),
                         context_headers[1]: breakdown
                }
            context.append(x)
    else:
        pass

    detailedtask = soup.find("div", {"id":"wrapper_DetailedWorkActivities"})
    detailedtask_li = detailedtask.findAll("li")
    detailedtask_text = [i.get_text() for i in detailedtask_li]

    data["title"] = title
    #data["moc"] = moc
    #data["military_type"] = military

    for elm in table2columns:
        data[elm] = makingTables(elm, content_area)
    for elm in list2columns:
        data[elm] = makinglist(elm, content_area)

    if len(tasks) > 0:
        data["tasks"] = tasks
    if len(context) > 0:
        data["work_context"] = context
    data["detailed_work_activities"] = detailedtask_text

    save_data(data)


# In[140]:


#from the main page with all jobs from all industries are listed
#it is in a table
main_page = "https://www.onetonline.org/find/industry?i=0&g=Go"
req = urllib.request.Request(main_page, headers={ 'User-Agent': 'Mozilla/5.0' })
html = urllib.request.urlopen(req).read()
soup=BeautifulSoup(html, 'html.parser')

rows = soup.select("td.report2ed > a ")


# In[141]:


#getting links of each job
#we keep only the ones with starting with https
hrefs = [row["href"] for row in rows if row["href"].startswith("http")]


# In[164]:


#if the link contains sub category job, then we click those links
for href in hrefs[638:]:
    page = href
    req = urllib.request.Request(page, headers={ 'User-Agent': 'Mozilla/5.0' })
    html = urllib.request.urlopen(req).read()
    soup=BeautifulSoup(html, 'html.parser')
    sub_cate = soup.find("div", {"class":"exclist"})
    if sub_cate != None:
        sub_occupation = soup.select("div.excitem > a")
        sub_jobs = [i["href"] for i in sub_occupation if i["href"].startswith("http")]
        for s in sub_jobs:
            scrape_page_wrapper(s)
    else:
        scrape_page_wrapper(href)


# In[2]:


## scrapping from the MOS
militaries = ["F", #air force
              "A", #army
              "C", #coast guard
              "M", #marine corp
              "N"] #navy

militaries_dic = {"F" : "Air_Force",
                  "A" : "Army",
                  "C" : "Coast_Guard",
                  "M" : "Marine_Corp",
                  "N" : "Navy"
                }

search_terms = [i for i in range(1, 10)]+list(string.ascii_lowercase)


# In[4]:


total_data = []
for m in militaries:
    for s in search_terms:
        mos_link = "https://www.onetonline.org/crosswalk/MOC?b={}&s={}&g=Go".format(m,s)
        print("\n", mos_link)
        req = urllib.request.Request(mos_link, headers={ 'User-Agent': 'Mozilla/5.0' })
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')

        print("finding table")
        table = soup.find("table", {"class":"occ"})
        if table == None:
            print("****",mos_link, " no search result")
            pass
        else:
            rows = soup.select("table.occ > tr")

            for row in rows:
                moc = row.find("td", {"class":"occcodebold"}).get_text()
                moc_desc = row.find("td", {"class":"occtitlebold"}).get_text()
                subtable = row.findAll("a")
                hrefs = [tr["href"] for tr in subtable if tr["href"].startswith("http")]
                links = [i for i in hrefs if i.startswith("http")]

                data = OrderedDict()
                data["moc"] = moc
                data["military_kind"] = militaries_dic[m]
                data["moc_desc"] = moc_desc.split("\n")[0]
                data["jobs"] = links

                total_data.append(data)

with open(str(moc_onet)+".json", "w") as file:
    json.dump(total_data, file)


# In[7]:


jobs = []
for total in total_data:
    for job in total["jobs"]:
        jobs.append(job)

jobs = list(set(jobs))




# In[30]:


new_list = []
for job in jobs:
    print(job)
    temp = OrderedDict()
    temp["job"] = job
    temp["moc"] = []
    for total in total_data:
        if job in total["jobs"]:
            temp["moc"] = temp["moc"]+[[total["moc"],
                                       total["military_kind"],
                                       total["moc_desc"]]]
        else:
            pass
    new_list.append(temp)


# In[40]:


moc = []
military_kind = []
moc_desc = []
jobs = []

for total in new_list:
    moc.append(total["moc"])
    jobs.append(total["job"])

df = pd.DataFrame({"moc":moc, "jobs":jobs})


# In[41]:


df.head(10)


# In[51]:


df2 = pd.DataFrame(df.moc.tolist(), index=df.jobs).stack().reset_index(level=1, drop=True)


# In[68]:


df3 = pd.DataFrame(df2)
df3["moc"] = df3.iloc[:, 0].apply(lambda x: x[0])
df3["military_kind"] = df3.iloc[:, 0].apply(lambda x: x[1])
df3["moc_desc"] = df3.iloc[:, 0].apply(lambda x: x[2])


# In[78]:


df3["job"] = df3.index


# In[80]:


df3 = df3[["job", "moc", "moc_desc", "military_kind", 0]]


# In[105]:


onet = os.listdir(os.path.join(os.getcwd(), "ONET"))


# In[109]:


onet2 = ["-".join(i.split("-")[0:2]).strip() for i in onet]


# In[119]:


jobcodes = [i[-1] for i in df3["job"].str.split("/")]


# In[134]:


counter = 0
jobcodes = list(set(jobcodes))
for jobcode in jobcodes:
    if jobcode in onet2:
        pass
    else:
        print(jobcode)
        counter+=1
print(counter)


# In[56]:


mos_link = "https://www.onetonline.org/crosswalk/MOC?b=F&s=1&g=Go"
print(mos_link)
#req = urllib.request.Request(mos_link, headers={ 'User-Agent': 'Mozilla/5.0' })
html = urllib.request.urlopen(mos_link).read()
soup = BeautifulSoup(html, 'html.parser')

table = soup.select("table.occ > tr")

if table == None:
    print(mos_link, " no search result")
else:
    pass

rows = soup.select("table.occ > tr")
for row in rows[10:20]:
    print("iterating through rows")
    moc = row.find("td", {"class":"occcodebold"}).get_text()
    moc_desc = row.find("td", {"class":"occtitlebold"}).get_text()
    print(len(subtable))
    #hrefs = [tr["href"] for tr in subtable if tr["href"].startswith("http")]
    #links = [i for i in hrefs if i.startswith("http")]
    #print(link)


# In[ ]:


len(table.findAll("td", {"class":"occcodebold"}))


# In[37]:


len(table.findAll("tr"))


# In[60]:


for row in rows[10:20]:
    print("iterating through rows")
    moc = row.find("td", {"class":"occcodebold"}).get_text()
    moc_desc = row.find("td", {"class":"occtitlebold"}).get_text()
    subtable = row.findAll("a")
    t = [i["href"] for i in subtable if i["href"].startswith("https")]
    print(len(t))


# In[ ]:
