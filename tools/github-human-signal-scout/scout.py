#!/usr/bin/env python3
"""Human-adoption-first GitHub discovery, stdlib Python 3.10+, GET only."""
import argparse
import json
import math
import os
import urllib.parse
import urllib.request

SEEDS=["deepseek harness QQ voice","OneBot TTS voice clone",
       "QQ CosyVoice GPT-SoVITS","QQ RVC voice","NapCat speech synthesis",
       "QQ AI companion voice","QQ 语音 克隆 音色","大肥鱼 声音"]
def get(path):
    headers={"Accept":"application/vnd.github+json","User-Agent":"human-signal-scout"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request("https://api.github.com"+path,headers=headers),timeout=25) as r:
        return json.load(r)
def popularity(row):
    social=sum(math.log1p(x["count"]) for x in row.get("social",[])
               if x.get("verified") is True and x.get("url","").startswith("https://")
               and type(x.get("count")) is int and x["count"]>=0
               and x.get("metric") in ("views","likes","comments","favorites"))
    return round(5*math.log1p(row["stars"])+7*math.log1p(row["forks"])
        +2*math.log1p(row.get("sample_comments") or 0)+1.4*social
        +(2 if row.get("releases") else 0)-(8 if row.get("archived") else 0),3)
def discover(queries,pages):
    found={};coverage=[]
    for query in queries:
        count=0;total=None;errors=[]
        for page in range(1,pages+1):
            q=urllib.parse.urlencode(dict(q=query,sort="stars",order="desc",per_page=100,page=page))
            try: result=get("/search/repositories?"+q)
            except Exception as e:
                errors.append(type(e).__name__+": "+str(e)[:160]);break
            if total is None: total=result.get("total_count")
            for r in result.get("items",[]):
                key=r["full_name"].lower()
                if key not in found:
                    found[key]=dict(name=r["full_name"],url=r["html_url"],
                        stars=r.get("stargazers_count",0),forks=r.get("forks_count",0),
                        issues_including_prs=r.get("open_issues_count",0),
                        archived=r.get("archived",False),description=r.get("description"),
                        queries=[query],social=[],sample_comments=None,releases=None)
                elif query not in found[key]["queries"]:found[key]["queries"].append(query)
            n=len(result.get("items",[]));count+=n
            if n<100:break
        coverage.append(dict(query=query,reported_total=total,retrieved=count,
            incomplete=bool(total and total>count),search_1000_cap=bool(total and total>1000),errors=errors))
    return list(found.values()),coverage
def enrich(r):
    base="/repos/"+r["name"]
    try:
        issues=get(base+"/issues?state=all&sort=updated&per_page=30")
        r["sample_comments"]=sum(x.get("comments",0) for x in issues if "pull_request" not in x)
    except Exception:pass
    try:r["releases"]=len(get(base+"/releases?per_page=30"))
    except Exception:pass
def main():
    p=argparse.ArgumentParser()
    p.add_argument("topic",nargs="?",default="QQ DSH 真人语音")
    p.add_argument("--query",action="append",default=[])
    p.add_argument("--pages",type=int,default=1)
    p.add_argument("--social",help="JSON: repo -> sourced URL, count, metric, verified")
    p.add_argument("--out",default="human-signal-report.json")
    a=p.parse_args()
    queries=list(dict.fromkeys((SEEDS if any(x in a.topic.lower() for x in ("qq","语音","dsh","tts")) else [a.topic,a.topic+" open source"])+a.query))
    rows,coverage=discover(queries,max(1,a.pages))
    rows.sort(key=popularity,reverse=True)
    for r in rows[:10]:enrich(r)
    if a.social:
        with open(a.social,encoding="utf8") as f: observations=json.load(f)
        for r in rows:
            r["social"]=[x for x in observations.get(r["name"],[])
                         if isinstance(x,dict) and x.get("url","").startswith("https://")
                         and type(x.get("count")) is int and x["count"]>=0]
    for r in rows:r["human_signal_score"]=popularity(r)
    rows.sort(key=lambda r:r["human_signal_score"],reverse=True)
    result={"queries":coverage,"candidate_count":len(rows),"repos":rows,
       "limits":["Search cap 1000 per query","Open issues include PRs",
         "Comment counts sampled from latest 30 issues","Social metrics must be source verified",
         "Stars and forks may be manipulated; popularity is not proof of quality"]}
    with open(a.out,"w",encoding="utf8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"out":a.out,"candidates":len(rows),"top":rows[:5]},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
