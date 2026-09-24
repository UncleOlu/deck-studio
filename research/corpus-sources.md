# Corpus sources

131 public decks studied for `corpus-findings.md`. The files are not in this repository; each row
gives the public URL. Rows marked **hold-out** were never coded and are reserved for the blind
discrimination test.

## Counts

| Genre | Decks | Hold-out |
|---|---|---|
| banking-board-book | 65 | 14 |
| consulting-client | 19 | 4 |
| consulting-published | 21 | 5 |
| public-sector-client | 26 | 5 |

Firm stratum: boutique 37, bulge 28, mbb 24, big4 24, other-consulting 18

## Collection method

- **SEC EDGAR**: `tools/corpus/edgar_fetch.py` — full-text search of SC 13E3 filings naming each of 12 advisors, then the EX-99.(c) exhibits with at least 6 page images; at most 5 books per advisor and 2 per company per run.
- **Aggregators** (Slideworks, SlideScience, Analyst Academy, Slidebook.io, 10X EBITDA, Alexander Jarvis): free, public material only, downloaded from the original public host where one existed. SlideScience returned 403; Slidebook.io and Alexander Jarvis gate their files, so they contributed notes only.
- **Public-sector client decks**: engagement deliverables published by public bodies (legislatures, councils, regulators, agencies).

## Decks

| Genre | Firm | Year | Deck type | Source | Hold-out |
|---|---|---|---|---|---|
| banking-board-book | BofA Securities | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/732834/000119312522278482/d273943dex99c2a.htm> | hold-out |
| banking-board-book | BofA Securities | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/732834/000119312522278482/d273943dex99c2b.htm> |  |
| banking-board-book | BofA Securities | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/732834/000119312522278482/d273943dex99c2c.htm> |  |
| banking-board-book | BofA Securities | 2023 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1575051/000114036123008785/ny20007737x1_exc7.htm> | hold-out |
| banking-board-book | BofA Securities | 2023 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1575051/000114036123008785/ny20007737x1_exc8.htm> |  |
| banking-board-book | BofA Securities | 2023 | buy-side M&A / roll-up | <https://www.10xebitda.com/wp-content/uploads/2025/02/Green-Plains-Discussion-Materials-2023.04.27.pdf> |  |
| banking-board-book | BofA Securities | 2024 | M&A / take-private | <https://www.10xebitda.com/wp-content/uploads/2025/02/Taro-Pharmaceuticals-Discussion-Materials-2024.01.17.pdf> |  |
| banking-board-book | Centerview | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1275283/000119312517168745/d352800dex99c18.htm> |  |
| banking-board-book | Centerview | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1275283/000119312517168745/d352800dex99c21.htm> |  |
| banking-board-book | Centerview | 2021 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1619954/000119312521295666/d218327dex99cv.htm> | hold-out |
| banking-board-book | Centerview | 2021 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1619954/000119312521295666/d218327dex99cvi.htm> | hold-out |
| banking-board-book | Centerview | 2021 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1619954/000119312521295666/d218327dex99cviii.htm> |  |
| banking-board-book | Centerview Partners | 2024 | take-private / fairness | <https://www.10xebitda.com/wp-content/uploads/2025/02/Endeavor-Discussion-Materials-2024.03.08.pdf> |  |
| banking-board-book | Citigroup | 2018 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1578932/000119312518210771/d671982dex99c3.htm> |  |
| banking-board-book | Citigroup | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1603016/000110465922094332/tm2220221d4_ex99-c2.htm> | hold-out |
| banking-board-book | Citigroup | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1603016/000110465922094332/tm2220221d4_ex99-c3.htm> |  |
| banking-board-book | Citigroup | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1603016/000110465922094332/tm2220221d4_ex99-c4.htm> |  |
| banking-board-book | Citigroup | 2024 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1753706/000114036124025205/ny20024121x7_excxii.htm> |  |
| banking-board-book | Evercore | 2016 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/929351/000157104916019206/t1602546_exc4.htm> |  |
| banking-board-book | Evercore | 2016 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/929351/000157104916019206/t1602546_exc5.htm> |  |
| banking-board-book | Evercore | 2016 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/929351/000157104916019206/t1602546_exc10.htm> |  |
| banking-board-book | Evercore | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1605725/000119312517219286/d383350dex99c2.htm> |  |
| banking-board-book | Evercore | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1605725/000119312517219286/d383350dex99c3.htm> |  |
| banking-board-book | Evercore | 2023 | sell-side M&A | <https://www.10xebitda.com/wp-content/uploads/2025/02/Evercore-Investment-Banking-Presentation-to-Diversey-01-Feb-2023.pdf> |  |
| banking-board-book | Goldman Sachs | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1275283/000119312517168745/d352800dex99c14.htm> |  |
| banking-board-book | Goldman Sachs | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1275283/000119312517168745/d352800dex99c15.htm> | hold-out |
| banking-board-book | Goldman Sachs | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1275283/000119312517168745/d352800dex99c22.htm> |  |
| banking-board-book | Goldman Sachs | 2018 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1517492/000114420418022494/tv491657_ex-c2.htm> |  |
| banking-board-book | Goldman Sachs | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465919001631/a18-38301_3ex99dc94.htm> |  |
| banking-board-book | Houlihan Lokey | 2018 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1385598/000104746918000136/a2234049zex-99_c2.htm> |  |
| banking-board-book | Houlihan Lokey | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/76321/000119312519270481/d814416dex99ci.htm> |  |
| banking-board-book | Houlihan Lokey | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/76321/000119312519270481/d814416dex99cii.htm> |  |
| banking-board-book | Houlihan Lokey | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/76321/000119312519270481/d814416dex99ciii.htm> |  |
| banking-board-book | Houlihan Lokey | 2026 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1829280/000114036126018703/ny20069883x4_exc1.htm> |  |
| banking-board-book | J.P. Morgan | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1275283/000119312517168745/d352800dex99c16.htm> |  |
| banking-board-book | J.P. Morgan | 2017 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1275283/000119312517168745/d352800dex99c17.htm> |  |
| banking-board-book | J.P. Morgan | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465919001631/a18-38301_3ex99dc96.htm> | hold-out |
| banking-board-book | J.P. Morgan | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465919001631/a18-38301_3ex99dc97.htm> |  |
| banking-board-book | J.P. Morgan | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465919001631/a18-38301_3ex99dc99.htm> |  |
| banking-board-book | J.P. Morgan | 2023 | buy-side M&A | <https://www.10xebitda.com/wp-content/uploads/2025/02/JPMorgan-Investment-Banking-Presentation-to-Searchlight-March-2023.pdf> |  |
| banking-board-book | Jefferies | 2018 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465918065862/a18-38301_2ex99dc41.htm> |  |
| banking-board-book | Jefferies | 2018 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465918065862/a18-38301_2ex99dc42.htm> |  |
| banking-board-book | Jefferies | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/883902/000110465922057808/tm228519d12_ex99-c1.htm> |  |
| banking-board-book | Jefferies | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/883902/000110465922057808/tm228519d12_ex99-c2.htm> |  |
| banking-board-book | Jefferies | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/883902/000110465922057808/tm228519d12_ex99-c3.htm> | hold-out |
| banking-board-book | Lazard | 2018 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1084201/000114420418004421/tv483956_ex99-c3.htm> |  |
| banking-board-book | Lazard | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1574135/000110465919059553/a19-19099_1ex99dc9.htm> | hold-out |
| banking-board-book | Lazard | 2021 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1619954/000119312521295666/d218327dex99ciii.htm> |  |
| banking-board-book | Lazard | 2021 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1619954/000119312521295666/d218327dex99civ.htm> |  |
| banking-board-book | Lazard | 2021 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1619954/000119312521295666/d218327dex99cvii.htm> |  |
| banking-board-book | Moelis | 2020 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/884940/000119312520097168/d891588dex99c2.htm> |  |
| banking-board-book | Moelis | 2020 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/884940/000119312520097168/d891588dex99c4.htm> |  |
| banking-board-book | Moelis | 2020 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/884940/000119312520097168/d891588dex99c5.htm> |  |
| banking-board-book | Moelis | 2023 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1651052/000110465923070127/tm2317104d3_ex99-c3.htm> |  |
| banking-board-book | Moelis | 2023 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1651052/000110465923070127/tm2317104d3_ex99-c4.htm> |  |
| banking-board-book | Morgan Stanley | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465919001631/a18-38301_3ex99dc95.htm> |  |
| banking-board-book | Morgan Stanley | 2019 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1598968/000110465919001631/a18-38301_3ex99dc98.htm> |  |
| banking-board-book | Morgan Stanley | 2020 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1633651/000119312520066868/d874077dex99c8.htm> |  |
| banking-board-book | Morgan Stanley | 2020 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1633651/000119312520066868/d874077dex99c9.htm> |  |
| banking-board-book | Morgan Stanley | 2022 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1295484/000110465922030885/tm2120623d8_exc-4.htm> |  |
| banking-board-book | PJT Partners | 2024 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1814329/000119312524133385/d681503dex99c2.htm> | hold-out |
| banking-board-book | PJT Partners | 2024 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1814329/000119312524133385/d681503dex99c3.htm> | hold-out |
| banking-board-book | PJT Partners | 2024 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1814329/000119312524133385/d681503dex99c4.htm> | hold-out |
| banking-board-book | PJT Partners | 2025 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1874944/000114036125009909/ny20040790x19_excviii.htm> | hold-out |
| banking-board-book | PJT Partners | 2025 | going-private board presentation | <https://www.sec.gov/Archives/edgar/data/1874944/000114036125009909/ny20040790x19_excix.htm> | hold-out |
| consulting-client | Accenture | 2019 | market study | <https://thinktv.ca/wp-content/uploads/2019/03/Accenture-Presentation-Feb-25.pdf> |  |
| consulting-client | Accenture | 2021 | market study | <https://www.nbnco.com.au/content/dam/nbn/documents/media-centre/media-statements/2021/accenture-consumer-value-report-2021.pdf.coredownload.pdf> |  |
| consulting-client | BCG | 2012 | market study | <https://www.nyc.gov/html/film/downloads/pdf/Media_in_NYC_2012.pdf> |  |
| consulting-client | BCG | 2012 | transformation | <https://www.nyc.gov/assets/nycha/downloads/pdf/BCG-report-NYCHA-Key-Findings-and-Recommendations-8-15-12vFinal.pdf> |  |
| consulting-client | BCG | 2013 | market study | <https://www.hewlett.org/wp-content/uploads/2016/08/The%20Open%20Educational%20Resources%20Ecosystem.pdf> |  |
| consulting-client | BCG | 2015 | market study | <https://wecreate.org.nz/wp-content/uploads/BCG-Victoria-Creative-Cultural-Economy-2015.pdf> |  |
| consulting-client | BCG | 2015 | market study | <https://www.nyc.gov/assets/mome/pdf/bcg-report-10.15.pdf> |  |
| consulting-client | Bain | 2014 | diagnostic | <https://news.syr.edu/wp-content/uploads/2017/04/Innovation-and-Opportunities-Assessment-Report-April-2014.pdf> |  |
| consulting-client | Bain | 2017 | market study | <https://altagamma.it/media/source/Altagamma%20Bain%20WW%20Markets%20Monitor%202017.pdf> |  |
| consulting-client | Deloitte | 2014 | strategy | <https://www.tillsonburg.ca/media/v3gnjreo/h21cb3ub_deloitte-it-strategic-review-2014.pdf> |  |
| consulting-client | Deloitte | 2015 | market study | <https://assets.publishing.service.gov.uk/media/5a80719b40f0b623026938a6/AAR_UK_Mapping.pdf> | hold-out |
| consulting-client | Deloitte | 2015 | diagnostic | <https://leads2025.nmsu.edu/pdf/NMSU-Recommendations-Report-Final.pdf> | hold-out |
| consulting-client | Deloitte | 2020 | strategy | <https://metrovancouver.org/boards/InvestVancouver/REP_2020-Jul-21_Item-5-2.pdf> |  |
| consulting-client | Deloitte | 2022 | diagnostic | <https://fletcherbuilding.com/assets/4-investor-centre/other-documents/fletcher-building-economic-uncertainty-analysis-deloitte-report.pdf> |  |
| consulting-client | McKinsey | 2010 | strategy | <https://about.usps.com/future-postal-service/mckinsey-march-2nd-presentation2.pdf> |  |
| consulting-client | McKinsey | 2010 | strategy | <https://about.usps.com/future-postal-service/mckinsey-usps-future-bus-model2.pdf> |  |
| consulting-client | McKinsey | 2020 | market study | <https://www.federalcitycouncil.org/wp-content/uploads/2020/12/McKinsey_Transportation.pdf> | hold-out |
| consulting-client | PwC | 2021 | market study | <https://www.iab.com/wp-content/uploads/2021/04/IAB_2020-Internet-Advertising-Revenue-Report-Webinar_4.7.21-PwC-1.pdf> |  |
| consulting-client | PwC | 2021 | market study | <https://www.acma.in/uploads/docmanager/PwC_PoV_E%20Mobility%20in%20India%20_May_21.pdf> | hold-out |
| consulting-published | Accenture | 2019 | market study | <https://bankingblog.accenture.com/wp-content/uploads/2019/05/Accenture_Financial-Services_Consumer-Study_2019_DACH.pdf> |  |
| consulting-published | Accenture | 2021 | market study | <https://riskandinsurance.com/wp-content/uploads/2021/12/TI-Accenture_PC_Underwriter_Survey-_vf.pdf> |  |
| consulting-published | Accenture | 2023 | market study | <https://www.accenture.com/content/dam/accenture/final/accenture-com/document/Accenture-PostalResearch-2023-for-com.pdf> |  |
| consulting-published | Bain | 2019 | transformation | <https://chicago.iabc.com/wp-content/uploads/2019/10/Bain-Presentation-Deck.pdf> | hold-out |
| consulting-published | EY | 2015 | market study | <https://eyfs.ie/wp-content/uploads/2015/03/European-Banking-Barometer-2015.pdf> | hold-out |
| consulting-published | EY | 2018 | market study | <https://eyfs.ie/wp-content/uploads/2018/08/EY-IFRS-9-impairment-banking-survey-2018-FINAL.pdf> |  |
| consulting-published | EY | 2020 | market study | <https://media2-col.corriereobjects.it/pdf/2020/dataroom/EY-Italian-infrastructure-barometer.pdf> |  |
| consulting-published | EY | 2022 | market study | <https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/insights/wealth-asset-management/documents/ey-2022-global-alternative-fund-survey.pdf> |  |
| consulting-published | EY | 2023 | market study | <https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/insights/banking-capital-markets/documents/ey-generative-ai-in-retail-and-commercial-banking.pdf> |  |
| consulting-published | EY | 2024 | market study | <https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/industries/wealth-asset-management/documents/ey-gl-genai-wam-survey-highlights-03-2024.pdf> |  |
| consulting-published | Kearney | 2022 | market study | <https://assets.website-files.com/5bd6cecc10ba2a724f7b2f22/620e238cf262fec630945ca5_20220216%20Customer%20Loyalty%20and%20Convenience%20MP%20V02.pdf> |  |
| consulting-published | Kearney | 2024 | market study | <https://www.luxuryroundtable.com/wp-content/uploads/2024/01/Kearney-Luxury-Outlook-Summit-2024-Jan.-17-Luxury-Roundtable-Presentation-Global-State-of-Luxury-2024.pdf> |  |
| consulting-published | Kearney | 2024 | strategy | <https://technobank.rs/wp-content/uploads/2024/04/09.35_Navigating-the-Digital-Frontier-Retail-Banking-Evolution-in-the-Age-of-AI_Kearney-SEE.pdf> | hold-out |
| consulting-published | McKinsey | 2018 | market study | <https://www.piie.com/sites/default/files/documents/madgavkar20181017ppt.pdf> |  |
| consulting-published | McKinsey | 2019 | transformation | <https://ibgcsitenovo.blob.core.windows.net/ibgcsitenovo/Eventos/Material/Rami%20Goldfajn_15h35-16h25.pdf> |  |
| consulting-published | McKinsey | 2022 | market study | <https://www.house.mn.gov/comm/docs/LjRJGpCGI0Soan8OsZqtqg.pdf> |  |
| consulting-published | Oliver Wyman | 2018 | market study | <https://www.oliverwyman.com/content/dam/oliver-wyman/v2/publications/2018/july/assessing-impact.pdf> |  |
| consulting-published | Oliver Wyman | 2018 | strategy | <https://www.oliverwyman.es/content/dam/oliver-wyman/Iberia/Customer%20Experience.pdf> |  |
| consulting-published | Oliver Wyman | 2020 | market study | <https://www.oliverwyman.com/content/dam/oliver-wyman/v2/publications/2020/March/COVID-19-Primer.pdf> | hold-out |
| consulting-published | Oliver Wyman | 2020 | market study | <https://www.oliverwyman.com/content/dam/oliver-wyman/ME/publications/COVID-19-Special-Primer.pdf> |  |
| consulting-published | PwC | 2023 | market study | <https://www.strategyand.pwc.com/a1/en/assets/pdf/ng-economic-outlook/nigeria-economic-outlook-october-2023-v1.pdf> | hold-out |
| public-sector-client | Accenture | 2010 | market-study | <https://about.usps.com/future-postal-service/accenture-presentation.pdf> |  |
| public-sector-client | Accenture (jointly with OFM program staff) | 2017 | transformation-steerco | <https://ofm.wa.gov/wp-content/uploads/sites/default/files/public/one/OneWA%20Program%20Blueprint%20Kickoff%20Event.pdf> |  |
| public-sector-client | Alvarez & Marsal | 2017 | due-diligence | <https://wyoleg.gov/InterimCommittee/2017/SGERPT1114.pdf> |  |
| public-sector-client | Bain & Company | 2009 | diagnostic | <https://bot.unc.edu/wp-content/uploads/sites/160/archives/PP%20709%20Bain%20Report.pdf> | hold-out |
| public-sector-client | Bain & Company | 2014 | diagnostic | <https://news.syr.edu/wp-content/uploads/2017/04/Innovation-and-Opportunities-Assessment-Report-April-2014.pdf> |  |
| public-sector-client | Boston Consulting Group | 2010 | market-study | <https://about.usps.com/future-postal-service/bcg-detailedpresentation.pdf> |  |
| public-sector-client | Boston Consulting Group | 2012 | market-study | <https://www.nyc.gov/html/film/downloads/pdf/Media_in_NYC_2012.pdf> |  |
| public-sector-client | Boston Consulting Group | 2012 | transformation-steerco | <https://www.nyc.gov/assets/nycha/downloads/pdf/BCG-report-NYCHA-Key-Findings-and-Recommendations-8-15-12vFinal.pdf> |  |
| public-sector-client | Boston Consulting Group | 2016 | strategy | <https://dallascityhall.com/government/Council%20Meeting%20Documents/loose-dogs-in-dallas-strategic-recommendations-to-improve-public-safety-and-animal-welfare_combined_083016.pdf> |  |
| public-sector-client | Deloitte | 2014 | strategy | <https://www.tillsonburg.ca/media/v3gnjreo/h21cb3ub_deloitte-it-strategic-review-2014.pdf> |  |
| public-sector-client | Deloitte | 2015 | market-study | <https://assets.publishing.service.gov.uk/media/5a80719b40f0b623026938a6/AAR_UK_Mapping.pdf> | hold-out |
| public-sector-client | Deloitte | 2015 | due-diligence | <https://leads2025.nmsu.edu/pdf/NMSU-Recommendations-Report-Final.pdf> | hold-out |
| public-sector-client | EY | 2018 | due-diligence | <https://webservices.ncleg.gov/ViewDocSiteFile/17082> |  |
| public-sector-client | EY | 2021 | strategy | <https://www.toronto.ca/legdocs/mmis/2021/gl/bgrd/backgroundfile-171711.pdf> |  |
| public-sector-client | KPMG | 2011 | diagnostic | <https://www.toronto.ca/legdocs/mmis/2011/ex/bgrd/backgroundfile-39686.pdf> |  |
| public-sector-client | KPMG | 2022 | due-diligence | <https://www.meaford.ca/wp-content/uploads/2026/06/service-delivery-review-final-report-may-30-2022.pdf> |  |
| public-sector-client | KPMG | 2024 | due-diligence | <https://huronshores.ca/wp-content/uploads/2026/01/KPMG-FInal-Report-Municipality-of-Huron-Shores-SDR-July29-24-ls.pdf> | hold-out |
| public-sector-client | McKinsey | 2010 | strategy | <https://about.usps.com/future-postal-service/mckinsey-march-2nd-presentation2.pdf> |  |
| public-sector-client | McKinsey | 2010 | diagnostic | <https://about.usps.com/future-postal-service/mckinsey-usps-future-bus-model2.pdf> |  |
| public-sector-client | McKinsey | 2012 | market-study | <https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/65626/7035-capturing-full-elec-eff-potential-edr.pdf> |  |
| public-sector-client | McKinsey | 2018 | strategy | <https://www.economy.gov.lb/media/11893/20181022-1228full-report-en.pdf> |  |
| public-sector-client | Oliver Wyman | 2023 | other | <https://www.insurance.ca.gov/0500-about-us/03-appointments/upload/Presentation1AActuarialSubcommitteeOverview.pdf> |  |
| public-sector-client | Oliver Wyman | 2024 | transformation-steerco | <https://gmcboard.vermont.gov/sites/gmcb/files/documents/20240619%20GMCB%20Board_State-level%20Recommendation_vPresented.pdf> |  |
| public-sector-client | Oliver Wyman | 2024 | strategy | <https://gmcboard.vermont.gov/sites/gmcb/files/documents/Act%20167%20Community%20Engagement_OW%20Exec%20Summary%20Report%20-%20revised%2010.21.2024.pdf> |  |
| public-sector-client | PwC | 2022 | strategy | <https://www.mbie.govt.nz/assets/new-zealand-hydrogen-regulatory-pathway-pwc-report.pdf> |  |
| public-sector-client | PwC | 2023 | diagnostic | <https://www.ofwat.gov.uk/wp-content/uploads/2023/06/PwC-Open-Data-Assessment-Report-Executive-Summary.pdf> | hold-out |

## Pitch-style discussion materials (added 2026-09-23)

8 more public decks studied for `pitchbook-findings.md`. They are not counted in the 131 above or used in
`corpus-stats.md`. None is hold-out; all were coded. Collection: EDGAR full-text search of SC 13E3 / SC 13E3/A / SC TO-T
filings for pitch phrases (process timeline, buyer universe, strategic alternatives), then the EX-99.(c) exhibits.

| Genre | Firm | Year | Deck type | Source | Hold-out |
|---|---|---|---|---|---|
| banking-pitch | Citigroup | 2012 | buyer-side discussion materials (process, valuation, qualifications) | <https://www.sec.gov/Archives/edgar/data/865754/000110465913028452/a13-7427_15ex99dc2.htm> | |
| banking-pitch | Evercore | 2013 | special-committee presentation (valuation, alternatives, process) | <https://www.sec.gov/Archives/edgar/data/826083/000119312513228037/d505474dex99c13.htm> | |
| banking-pitch | Goldman Sachs | 2021 | strategic-alternatives discussion materials | <https://www.sec.gov/Archives/edgar/data/1752836/000119312522213042/d377047dex99c6.htm> | |
| banking-pitch | Goldman Sachs / Lincoln International | 2021 | sale-process kick-off materials | <https://www.sec.gov/Archives/edgar/data/1752836/000119312522213042/d377047dex99c7.htm> | |
| banking-pitch | J.P. Morgan | 2012 | preliminary special-committee presentation | <https://www.sec.gov/Archives/edgar/data/826083/000119312513134621/d505474dex99c29.htm> | |
| banking-pitch | Jefferies | 2023 | preliminary materials for discussion (situation, valuation, next steps) | <https://www.sec.gov/Archives/edgar/data/1528930/000110465923078458/tm2317758d5_ex-c1.htm> | |
| banking-pitch | Lazard | 2020 | special-committee kick-off (valuation approach, process timeline, tactics) | <https://www.sec.gov/Archives/edgar/data/1740547/000119312521048264/d22741dex99c7.htm> | |
| banking-pitch | Morgan Stanley | 2022 | special-committee process update and considerations | <https://www.sec.gov/Archives/edgar/data/1664998/000119312522307513/d323857dex99ciii.htm> | |
