import pandas as pd
import statsmodels.api as sm
import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
names=['CDX HY '+str(i)+'Y SPREAD.xlsx' for i in [3,5,7,10]]
HY_list=[pd.read_excel('E:\正式文件\BAM\Liquidity data\\'+names[i],header=None,names=['Character','Date','Bid','Ask']) for i in range(len(names))]
HY_list=[i.dropna().drop(['Character'],axis=1) for i in HY_list]
for i in HY_list:
    i['Spread']=i['Bid']-i['Ask']
VIX=pd.read_excel('E:\正式文件\BAM\Liquidity data\VIX.xlsx',header=None,names=['Character','Date','VIX'],skiprows=[0])
VIX=VIX.drop(['Character'],axis=1).dropna()
tenyear_yield=pd.read_csv('E:\HistoricalPrices_10Y.csv',header=None,skiprows=[0],names=['Date']+['10Y_'+i for i in ['Open','High','Low','Close']])
oneyear_yield=pd.read_csv('E:\HistoricalPrices_1Y.csv',header=None,skiprows=[0],names=['Date']+['1Y_'+i for i in ['Open','High','Low','Close']])
whole_yield=tenyear_yield.merge(oneyear_yield,how='inner',left_on='Date',right_on='Date')
whole_yield['curve_spread']=whole_yield['10Y_Close']-whole_yield['1Y_Close']
def date_conversion(x):
    temp=x.split('/')
    temp[-1]='20'+temp[-1]
    temp_date='/'.join(temp)
    return datetime.datetime.strptime(temp_date,'%m/%d/%Y')
whole_yield['Date']=whole_yield['Date'].apply(lambda x:date_conversion(x))
for i in HY_list:
    DF_temp=i.merge(VIX,how='inner',left_on='Date',right_on='Date')
    DF_temp=DF_temp.merge(whole_yield,how='inner',left_on='Date',right_on='Date')
    X=DF_temp[['Spread','curve_spread']].values
    #print(sm.tsa.adfuller(X))
    X=sm.add_constant(X)
    Y=DF_temp['VIX'].astype(float).values
    model=sm.OLS(Y,X)
    model=model.fit()
    print(model.summary())
    #print(DF_temp)
#print(HY_list[0])
Aim='STCENT 21st Century Fox America, Inc. STCENT (2) 3.7 15Sep24 US90131HAE53 SNRFOR AET Aetna Inc. AET 6.625 15Jun36 BondCall US00817YAF51 SNRFOR AEP AMERICAN ELECTRIC POWER COMPANY, INC. AEP 2.95 15Dec22 US025537AG68 SNRFOR AXP American Express Company AXP (4) 2.65 02Dec22 US025816BD05 SNRFOR AIG American International Group, Inc. AIG 6.25 01May36 Struc US026874AZ07 SNRFOR AMGN Amgen Inc. AMGN 2.2 22May19 US031162BU36 SNRFOR APC ANADARKO PETROLEUM CORPORATION APC 6.95 15Jun19 US032511BF31 SNRFOR ANDEAVAA Andeavor ANDEAVAA (5) 4.75 15Dec23 US03349MAC91 SNRFOR APA APACHE CORPORATION APA 3.25 15Apr22 US037411AZ87 SNRFOR ARW ARROW ELECTRONICS, INC. ARW 6 01Apr20 US042735BA76 SNRFOR DEXBB-AGM ASSURED GUARANTY MUNICIPAL CORP. SNRFOR ATTINC AT&T Inc. ATTINC 2.45 30Jun20 US00206RCL42 SNRFOR AZO AutoZone, Inc. AZO 2.5 15Apr21 US053332AS14 SNRFOR AVT Avnet, Inc. AVT 4.875 01Dec22 US053807AR45 SNRFOR ABX BARRICK GOLD CORPORATION ABX 5.8 15Nov34 US067901AA64 SNRFOR BAX Baxter International Inc. BAX 1.7 15Aug21 US071813BR97 SNRFOR BRK Berkshire Hathaway Inc. BRK 2.75 15Mar23 US084670BR84 SNRFOR BBY Best Buy Co., Inc. BBY 5.5 15Mar21 US086516AL50 SNRFOR HRB-Fllc Block Financial LLC HRB-Fllc 5.5 01Nov22 Struc US093662AE40 SNRFOR BSX Boston Scientific Corporation BSX 6 15Jan20 US101137AK32 SNRFOR BMY Bristol-Myers Squibb Company BMY 6.8 15Nov26 US110122AB49 SNRFOR CPB CAMPBELL SOUP COMPANY CPB 4.25 15Apr21 US134429AW93 SNRFOR CNATUR CANADIAN NATURAL RESOURCES LIMITED CNATUR 3.45 15Nov21 US136385AR22 SNRFOR CAH Cardinal Health, Inc. CAH 4.625 15Dec20 US14149YAT55 SNRFOR CCL CARNIVAL CORPORATION CCL 6.65 15Jan28 US143658AH53 SNRFOR CAT Caterpillar Inc. CAT 3.9 27May21 US149123BV25 SNRFOR CBSCOR CBS Corporation CBSCOR 4.3 15Feb21 US124857AE30 SNRFOR CHUBLIM Chubb Limited CHUBINA 8.875 15Aug29 US00440EAC12 SNRFOR CMCSA Comcast Corporation CMCSA 5.7 01Jul19 BondCall US20030NAZ42 SNRFOR CONABRA Conagra Brands, Inc. CONABRA 7 01Oct28 US205887AR36 SNRFOR COP ConocoPhillips COP (3) 5.9 15Oct32 US20825CAF14 SNRFOR COX-CommInc Cox Communications, Inc. COX-CommInc 6.8 01Aug28 US224044AN72 SNRFOR CSX CSX Corporation CSX 3.7 01Nov23 US126408GZ04 SNRFOR CVSHEA CVS Health Corporation CVSHEA 2.125 01Jun21 US126650CT50 SNRFOR DRI Darden Restaurants, Inc. DRI 3.85 01May27 US237194AL90 SNRFOR DE Deere & Company DE 4.375 16Oct19 US244199BC83 SNRFOR DVN Devon Energy Corporation DVN 7.95 15Apr32 US251799AA02 SNRFOR DOMINEN Dominion Energy, Inc. DOMINEN 2.75 15Jan22 US25746UCR86 SNRFOR DOMC Domtar Corporation DOMC 4.4 01Apr22 US257559AH77 SNRFOR DUKECO Duke Energy Carolinas, LLC DUKECO 6.1 01Jun37 US26442CAA27 SNRFOR DXCTEC DXC TECHNOLOGY COMPANY DXCTEC 4.45 18Sep22 US23355LAA44 SNRFOR DD E. I. du Pont de Nemours and Company DD 2.8 15Feb23 US263534CK37 SNRFOR EMN Eastman Chemical Company EMN 7.6 01Feb27 US277432AD23 SNRFOR ENB Enbridge Inc. ENB 3.5 10Jun24 US29250NAH89 SNRFOR ECACN ENCANA CORPORATION ECACN 6.5 15May19 US292505AH79 SNRFOR ENERTRAB Energy Transfer Partners, L.P. ENERTRAB 4.15 01Oct20 US29273RAX70 SNRFOR EQR-ERPOperLP ERP Operating Limited Partnership EQR-ERPOperLP 4.625 15Dec21 US26884AAZ66 SNRFOR EXC Exelon Corporation EXC 5.15 01Dec20 US210371AL43 SNRFOR FE FirstEnergy Corp. FE 7.375 15Nov31 US337932AC13 SNRFOR F Ford Motor Company F 4.346 08Dec26 US345370CR99 SNRFOR GE General Electric Company GE 2.7 09Oct22 US369604BD45 SNRFOR GIS General Mills, Inc. GIS 3.15 15Dec21 US370334BM56 SNRFOR HAL HALLIBURTON COMPANY HAL-EnSvcs 8.75 15Feb21 US406216AH42 SNRFOR HESS Hess Corporation HESS 3.5 15Jul24 US42809HAF47 SNRFOR HON Honeywell International Inc. HON 5.7 15Mar36 BondCall US438516AR73 SNRFOR HOSHOT-HSTRES Host Hotels & Resorts, L.P. HOSHOT-HSTRES 4.75 01Mar23 US44107TAT34 SNRFOR HPINCAA HP Inc. HPINCAA 4.65 09Dec21 US428236BV43 SNRFOR IR-NJ Ingersoll-Rand Company IR-NJ 9 15Aug21 US456866AG74 SNRFOR IBM International Business Machines Corporation IBM 1.625 15May20 US459200HM60 SNRFOR AIG-IntLeaseFin INTERNATIONAL LEASE FINANCE CORPORATION AIG-IntLeaseFin 8.25 15Dec20 US459745GF62 SNRFOR IP INTERNATIONAL PAPER COMPANY IP 7.5 15Aug21 Struc US460146CE11 SNRFOR JNJ Johnson & Johnson JNJ 1.65 01Mar21 US478160BS27 SNRFOR JOHCON JOHNSON CONTROLS INTERNATIONAL PUBLIC LIMITED COMPANY JOHCON 5 30Mar20 US478375AD00 SNRFOR KINDERM Kinder Morgan, Inc. KINDERM 3.05 01Dec19 US49456BAE11 SNRFOR KSS Kohl\'s Corporation KSS 4 01Nov21 US500255AR59 SNRFOR KRAFHEI Kraft Heinz Foods Company KRAFHEI 6.375 15Jul28 US423074AF08 SNRFOR LNC Lincoln National Corporation LNC 6.25 15Feb20 US534187AY52 SNRFOR LMT Lockheed Martin Corporation LMT 4.25 15Nov19 US539830AT67 SNRFOR LTR Loews Corporation LTR 6 01Feb35 US540424AP38 SNRFOR LOW Lowe\'s Companies, Inc. LOW 4.625 15Apr20 US548661CQ89 SNRFOR M Macy\'s, Inc. M-RHI 3.45 15Jan21 US55616XAN75 SNRFOR MMC MARSH & McLENNAN COMPANIES, INC. MMC 5.875 01Aug33 US571748AK86 SNRFOR MCD McDONALD\'S CORPORATION MCD 2.75 09Dec20 US58013MEX83 SNRFOR MCK McKesson Corporation MCK 7.65 01Mar27 US581557AM75 SNRFOR MET MetLife, Inc. MET 4.75 08Feb21 US59156RAX61 SNRFOR MONDINT Mondelez International, Inc. MONDINT 4 01Feb24 US609207AB14 SNRFOR MOTSOL Motorola Solutions, Inc. MOTSOL 7.5 15May25 US620076AH21 SNRFOR NRUC National Rural Utilities Cooperative Finance Corporation NRUC 8 01Mar32 US637432CT02 SNRFOR NEWEBRA Newell Brands Inc. NEWEBRA 3.85 01Apr23 US651229AV81 SNRFOR NEM Newmont Mining Corporation NEM 5.875 01Apr35 US651639AE60 SNRFOR JWN Nordstrom, Inc. JWN 6.95 15Mar28 US655664AH33 SNRFOR NSC NORFOLK SOUTHERN CORPORATION NSC 3.25 01Dec21 US655844BG28 SNRFOR NORGRM Northrop Grumman Corporation NOC-SysCorp (3) 7.75 15Feb31 US666807AW21 SNRFOR OMC Omnicom Group Inc. OMC 4.45 15Aug20 US682134AC59 SNRFOR PACKAM Packaging Corporation of America PACKAM 3.9 15Jun22 US695156AP42 SNRFOR PFE Pfizer Inc. PFE 2.2 15Dec21 US717081DZ31 SNRFOR PRU Prudential Financial, Inc. PRU 7.375 15Jun19 US74432QBG91 SNRFOR DGX Quest Diagnostics Incorporated DGX 2.5 30Mar20 US74834LAW00 SNRFOR RTN Raytheon Company RTN 7.2 15Aug27 US755111AF81 SNRFOR RAI Reynolds American Inc. RAI 4.85 15Sep23 US761713AY21 SNRFOR RCL ROYAL CARIBBEAN CRUISES LTD. RCL 5.25 15Nov22 US780153AU63 SNRFOR R Ryder System, Inc. R 2.55 01Jun19 US78355HJW07 SNRFOR SRE Sempra Energy SRE 4.05 01Dec23 US816851AU37 SNRFOR SPG-LP Simon Property Group, L.P. SPG-LP 4.375 01Mar21 US828807CF26 SNRFOR LUV Southwest Airlines Co. LUV 2.65 05Nov20 US844741BB35 SNRFOR TGT Target Corporation TGT 3.875 15Jul20 US87612EAV83 SNRFOR ALL The Allstate Corporation ALL 3.15 15Jun23 US020002AZ47 SNRFOR BA THE BOEING COMPANY BA 8.75 15Aug21 US097023AD79 SNRFOR DOW The Dow Chemical Company DOW 7.375 01Nov29 US260543BJ10 SNRFOR HD The Home Depot, Inc. HD 5.875 16Dec36 BondCall US437076AS19 SNRFOR KR THE KROGER CO. KR 6.15 15Jan20 US501044CH20 SNRFOR SHW The Sherwin-Williams Company SHW 7.375 01Feb27 US824348AL09 SNRFOR DIS The Walt Disney Company DIS 2.55 15Feb22 US25468PCT12 SNRFOR TSN Tyson Foods, Inc. TSN 4.5 15Jun22 US902494AT07 SNRFOR UNP Union Pacific Corporation UNP 6.625 01Feb29 US907818CF33 SNRFOR UPS United Parcel Service, Inc. UPS-AmericaInc 8.375 01Apr30 US911308AB04 SNRFOR UNH UnitedHealth Group Incorporated UNH 3.35 15Jul22 US91324PCN06 SNRFOR VLOC Valero Energy Corporation VLOC 8.75 15Jun30 US91913YAB65 SNRFOR VRZN Verizon Communications Inc. VRZN 2.55 17Jun19 US92343VCB80 SNRFOR VIAINC Viacom Inc. VIAINC 6.875 30Apr36 Struc US925524AX89 SNRFOR WALMINC WALMART INC. WALMINC 5.875 05Apr27 US931142CH46 SNRFOR WESTMWV WestRock MWV, LLC WESTMWV 7.95 15Feb31 US961548AY02 SNRFOR WY Weyerhaeuser Company WY 7.125 15Jul23 US962166AS33 SNRFOR WHR Whirlpool Corporation WHR 4.85 15Jun21 US96332HCD98 SNRFOR XRX XEROX CORPORATION XRX 2.75 01Sep20 US984121CK78 SNRFOR XLITLTD XLIT Ltd. XLITLTD 6.25 15May27 US98372PAK49 SNRFOR'
company=Aim.split('SNRFOR')
company=[i.strip(' ').split(' ')[0] for i in company]
company_data={}
for i in company:
    if i!='':
        company_data[i]=['https://finance.yahoo.com/quote/%s/history?p=%s'%(i,i)]
        company_data[i].append('https://finance.yahoo.com/quote/%s/profile?p=%s'%(i,i))
print(company_data)
for name,data in company_data.items():
    r=requests.get(data[1])
    data=r.text
    soup=BeautifulSoup(data,'lxml')
    #print(soup)
    for ind,span in enumerate(soup.find_all('span')):
        if span.get_text()=='Sector':
            print(soup.find_all('span')[ind+1].get_text())

options=webdriver.ChromeOptions()
prefs={'profile.default_content_settings.popups': 0, 'download.default_directory': 'E:\\',"profile.default_content_setting_values.automatic_downloads":30}
options.add_experimental_option('prefs',prefs)
driver=webdriver.Chrome(executable_path='E:/chromedriver.exe',chrome_options=options)
list=['Energy','Basic Materials','Industrials','Consumer Discretionary','Consumer Staples','Healthcare','Financial','Information Technology','Communications','Utilities','Real Estate']