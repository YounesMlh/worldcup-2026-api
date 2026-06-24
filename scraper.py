import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
response = requests.get(URL, headers=headers)

def scrape_matches():
    if response.status_code != 200:
        print("خطأ في الاتصال بالموقع")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    matches_list = []

    # البحث عن القوالب الكلاسيكية للمباريات في ويكيبيديا (footballbox)
    match_blocks = soup.find_all(["div", "table"], class_=["footballbox", "vevent"])

    # إذا لم يجد الكلاسات السابقة، سنبحث عن بنية الجداول البديلة التي تحتوي على التوقيت والفرق
    if not match_blocks:
        match_blocks = soup.find_all("table", class_="collapsible")

    for match in match_blocks:
        try:
            # طريقة ويكيبيديا القياسية لاستخراج الفرق والنتيجة
            home_elem = match.find(class_=["fhome", "team-home", "home"])
            away_elem = match.find(class_=["faway", "team-away", "away"])
            score_elem = match.find(class_=["fscore", "score"])

            # إذا وجدنا العناصر، نقوم باستخراج النصوص وتنظيفها
            if home_elem and away_elem:
                home_team = home_elem.text.strip()
                away_team = away_elem.text.strip()
                score = score_elem.text.strip() if score_elem else "v"

                # إزالة أي مساحات زائدة أو أقواس
                score = score.split('\n')[0].strip()

                matches_list.append({
                    "home_team": home_team,
                    "score": score,
                    "away_team": away_team
                })
        except Exception as e:
            continue
            
    return matches_list

if __name__ == "__main__":
    data = scrape_matches()
    print(f"📋 تم سحب {len(data)} مباراة بنجاح!")
    if data:
        df = pd.DataFrame(data)
        print("\nعينة من المباريات الحية المكتشفة:")
        print(df.head(10))