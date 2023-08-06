# -*- coding: utf-8 -*-

"""Common configuration constants
"""
from Products.Archetypes.public import DisplayList

###########################################################################
## ACTED only change what is between the ######## lines !!!!!
## ivan.price@acted.org   14/6/2010
## 
## After changing this file you need to restart plone !

theYears = range(1995,2015)

theDonors = []
theDonors.append((u'Bilateral Cooperations',u'Bilateral Cooperations'))
theDonors.append((u'--- All',u'All Bilateral Cooperations'))
theDonors.append((u'--- Afghanistan',u'Afghanistan'))
theDonors.append((u'------- Afghan Government',u'Afghan Government'))
theDonors.append((u'------- Ministry of Agriculture, Irrigation and Livestock (MAIL)',u'Ministry of Agriculture, Irrigation and Livestock (MAIL)'))
theDonors.append((u'------- Ministry of Social Affairs',u'Ministry of Social Affairs'))
theDonors.append((u'------- Minister of Counter Narcotics',u'Minister of Counter Narcotics'))
theDonors.append((u'------- Other:',u'Other Afghanistan'))
theDonors.append((u'----------- NOR CIMIC',u'NOR CIMIC'))
theDonors.append((u'--- Canada',u'Canada'))
theDonors.append((u'------- CIDA/ACDI',u'CIDA/ACDI'))
theDonors.append((u'------- Embassies',u'Embassies - Canada'))
theDonors.append((u'--- Chad',u'Chad'))
theDonors.append((u'--- Congo Brazzaville',u'Congo Brazzaville'))
theDonors.append((u'--- Denmark',u'Denmark'))
theDonors.append((u'------- DANIDA',u'DANIDA'))
theDonors.append((u'--- DRC',u'DRC'))
theDonors.append((u'--- France',u'France'))
theDonors.append((u'------- CIAA',u'CIAA'))
theDonors.append((u'------- Centre de Crise/DAH',u'Centre de Crise/DAH'))
theDonors.append((u'------- Decentralised Cooperation',u'Decentralised Cooperation'))
theDonors.append((u'----------- Cités Unies France',u'Cités Unies France'))
theDonors.append((u'----------- Ville de Paris',u'Ville de Paris'))
theDonors.append((u'----------- Other:',u'Other France Decentralised Cooperation'))
theDonors.append((u'--------------- Agence de l\'eau Adour-Garonne',u'Agence de l\'eau Adour-Garonne'))
theDonors.append((u'--------------- Communautés de Commune de Kreiz Breiz',u'Communautés de Communede Kreiz Breiz'))
theDonors.append((u'--------------- Commune de Guillers',u'Communede Guillers'))
theDonors.append((u'--------------- Commune de Hanvec',u'Commune de Hanvec'))
theDonors.append((u'--------------- Commune de Saint Briac',u'Communede Saint Briac'))
theDonors.append((u'--------------- Commune d\'Ornex',u'Commune d\'Ornex'))
theDonors.append((u'--------------- Conseil Général des Côtes d\'Armor',u'Conseil Général des Côtes d\'Armor'))
theDonors.append((u'--------------- Conseil Régional de Bretagne',u'Conseil Régional de Bretagne'))
theDonors.append((u'--------------- Ile de France (Région)',u'Ile de France (Région)'))
theDonors.append((u'--------------- Ville de Fougères',u'Ville de Fougères'))
theDonors.append((u'------- Embassies',u'Embassies - France'))
theDonors.append((u'----------- French MFA',u'French MFA'))
theDonors.append((u'------- Other',u'Other France'))
theDonors.append((u'--- Germany',u'Germany'))
theDonors.append((u'------- Embassies',u'Embassies - Germany'))
theDonors.append((u'------- German MFA',u'German MFA'))
theDonors.append((u'------- GTZ',u'GTZ'))
theDonors.append((u'--- Iraq',u'Iraq'))
theDonors.append((u'------- CPA',u'CPA'))
theDonors.append((u'--- Iran',u'Iran'))
theDonors.append((u'------- Embassies',u'Embassies - Iran'))
theDonors.append((u'--- Japan',u'Japan'))
theDonors.append((u'------- Embassies',u'Embassies - Japan'))
theDonors.append((u'------- JICA',u'JICA'))
theDonors.append((u'--- Latvia',u'Latvia'))
theDonors.append((u'--- Netherlands',u'Netherlands'))
theDonors.append((u'------- Embassies',u'Embassies - Netherlands'))
theDonors.append((u'--- Nicaragua',u'Nicaragua'))
theDonors.append((u'--- Norway ',u'Norway'))
theDonors.append((u'------- NORAD',u'NORAD'))
theDonors.append((u'------- Royal Norwegian Embassy (RNE)',u'Royal Norwegian Embassy (RNE)'))
theDonors.append((u'--- Spain',u'Spain'))
theDonors.append((u'------- AECID',u'AECID'))
theDonors.append((u'--- Sweden',u'Sweden'))
theDonors.append((u'------- SIDA',u'SIDA'))
theDonors.append((u'--- Switzerland',u'Switzerland'))
theDonors.append((u'------- SDC/DDC',u'SDC/DDC'))
theDonors.append((u'--- Tajikistan ',u'Tajikistan'))
theDonors.append((u'--- Turkey',u'Turkey'))
theDonors.append((u'--- UK',u'UK'))
theDonors.append((u'------- DFID',u'DFID'))
theDonors.append((u'------- Embassies',u'Embassies - UK'))
theDonors.append((u'--- USA',u'USA'))
theDonors.append((u'------- BPRM',u'BPRM'))
theDonors.append((u'------- Embassies',u'Embassies - USA'))
theDonors.append((u'------- OFDA',u'OFDA'))
theDonors.append((u'------- USAID',u'USAID'))
theDonors.append((u'------- ARD',u'ARD'))
theDonors.append((u'------- Chemonics',u'Chemonics'))
theDonors.append((u'------- International Fertilizer Development Center (IFDC)',u'International Fertilizer Development Center (IFDC)'))
theDonors.append((u'------- UMCOR',u'UMCOR'))
theDonors.append((u'------- Other',u'Other USA'))
theDonors.append((u'--- Other',u'Other Bilateral Cooperations'))
theDonors.append((u'European Commission',u'European Commission'))
theDonors.append((u'--- All',u'All'))
theDonors.append((u'--- ECHO',u'ECHO'))
theDonors.append((u'--- EuropeAid (AidCo)',u'EuropeAid (AidCo)'))
theDonors.append((u'--- Other:',u'Other European Commission'))
theDonors.append((u'------- Euronaid',u'Euronaid'))
theDonors.append((u'------- Task Force',u'Task Force'))
theDonors.append((u'International Organisations',u'International Organisations'))
theDonors.append((u'--- All',u'All'))
theDonors.append((u'--- ADB/BAD',u'ADB/BAD'))
theDonors.append((u'--- ASEAN',u'ASEAN'))
theDonors.append((u'--- EBRD/BERD',u'EBRD/BERD'))
theDonors.append((u'--- Global Fund',u'Global Fund'))
theDonors.append((u'--- IOM / OIM',u'IOM / OIM'))
theDonors.append((u'--- OSCE',u'OSCE'))
theDonors.append((u'------- WB / BM',u'WB / BM'))
theDonors.append((u'----------- MISFA',u'MISFA'))
theDonors.append((u'----------- NSP',u'NSP'))
theDonors.append((u'----------- Other',u'Other WB/BM'))
theDonors.append((u'--- Other',u'Other International Organisations'))
theDonors.append((u'Private Cooperation',u'Private Cooperation'))
theDonors.append((u'--- All',u'All'))
theDonors.append((u'--- ABN-AMRO',u'ABN-AMRO'))
theDonors.append((u'--- Aga Khan Foundation',u'Aga Khan Foundation'))
theDonors.append((u'--- Assistance Foundation',u'Assistance Foundation'))
theDonors.append((u'--- Association Enfants Démunis Kareen Mane (AED)',u'Association Enfants Démunis Kareen Mane (AED)'))
theDonors.append((u'--- CARE',u'CARE'))
theDonors.append((u'--- Caritas',u'Caritas'))
theDonors.append((u'--- Centre d\'Etude et de Coopération Internationale (CECI)',u'Centre d\'Etude et de Coopération Internationale (CECI)'))
theDonors.append((u'--- Chemonics',u'Chemonics'))
theDonors.append((u'--- Cooperative Housing Foundation (CHF)',u'Cooperative Housing Foundation (CHF)'))
theDonors.append((u'--- Children Aid',u'Children Aid'))
theDonors.append((u'--- Christian Aid',u'Christian Aid'))
theDonors.append((u'--- Clinton Foundation',u'Clinton Foundation'))
theDonors.append((u'--- Concern',u'Concern'))
theDonors.append((u'--- Dan Church Aid (DCA)',u'Dan Church Aid (DCA)'))
theDonors.append((u'--- Eurasian Foundation of Central Asia',u'Eurasian Foundation of Central Asia'))
theDonors.append((u'--- Family Health International',u'Family Health International'))
theDonors.append((u'--- Fondation de France',u'Fondation de France'))
theDonors.append((u'--- France Culture',u'France Culture'))
theDonors.append((u'--- GTZ',u'GTZ'))
theDonors.append((u'--- HIVOS',u'HIVOS'))
theDonors.append((u'--- Interchurch Organisation for Development Cooperation (ICCO)',u'Interchurch Organisation for Development Cooperation (ICCO)'))
theDonors.append((u'--- International Rescue Committee (IRC)',u'International Rescue Committee (IRC)'))
theDonors.append((u'--- Musée Guimet',u'Musée Guimet'))
theDonors.append((u'--- Norwegian Church Aid / Norwegian Refugee Council (NCA / NRC)',u'Norwegian Church Aid / Norwegian Refugee Council (NCA/NRC)'))
theDonors.append((u'--- Novib',u'Novib'))
theDonors.append((u'--- People In Need (PIN)',u'People In Need (PIN)'))
theDonors.append((u'--- Red Cross / Croix Rouge / IFRC / FICR',u'Red Cross / Croix Rouge / IFRC / FICR'))
theDonors.append((u'--- Reuters',u'Reuters'))
theDonors.append((u'--- ShelterBox UK',u'ShelterBox UK'))
theDonors.append((u'--- Soros Foundation',u'Soros Foundation'))
theDonors.append((u'--- The Christensen Fund (TCF)',u'The Christensen Fund (TCF)'))
theDonors.append((u'--- United Methodist Committee on Relief (UMCOR)',u'United Methodist Committeeon Relief (UMCOR)'))
theDonors.append((u'--- Voix de l\'Enfant (VDE)',u'Voix de l\'Enfant (VDE)'))
theDonors.append((u'--- Vétérinaires Sans Frontières-Belgium (VSF)',u'Vétérinaires Sans Frontières-Belgium (VSF)'))
theDonors.append((u'--- Warchild',u'Warchild'))
theDonors.append((u'--- Welthungerhilfe (WHH)',u'Welthungerhilfe (WHH)'))
theDonors.append((u'--- Other:',u'Other Private Cooperation'))
theDonors.append((u'------- Abbé Pierre',u'Abbé Pierre'))
theDonors.append((u'------- Aid and Relief (AAR)',u'Aid and Relief (AAR)'))
theDonors.append((u'------- AREVA',u'AREVA'))
theDonors.append((u'------- BMB Mott Mac Donald',u'BMB Mott Mac Donald'))
theDonors.append((u'------- Délégation Archéologique Française en Afghanistan (DAFA)',u'Délégation Archéologique Françaiseen Afghanistan (DAFA)'))
theDonors.append((u'------- Diageo',u'Diageo'))
theDonors.append((u'------- ELF Aquitaine',u'ELF Aquitaine'))
theDonors.append((u'------- ELF Congo',u'ELF Congo'))
theDonors.append((u'------- Emmaüs',u'Emmaüs'))
theDonors.append((u'------- Foundation for Development Cooperation – Singapore (FDC)',u'Foundation for Development Cooperation – Singapore (FDC)'))
theDonors.append((u'------- GOAL',u'GOAL'))
theDonors.append((u'------- Goethe Institute',u'Goethe Institute'))
theDonors.append((u'------- Islamic Relief',u'Islamic Relief'))
theDonors.append((u'------- Lions\' Club',u'Lions\' Club'))
theDonors.append((u'------- PRT Paktia',u'PRT Paktia'))
theDonors.append((u'------- Restorers Without Borders / Restaurateurs Sans Frontières',u'Restorers Without Borders/Restaurateurs Sans Frontières'))
theDonors.append((u'------- Société Protectrice des Animaux et de la Nature (SPANA)',u'Société Protectrice des Animaux et de la Nature (SPANA)'))
theDonors.append((u'------- Sri Lanka Nel Cuore',u'Sri Lanka Nel Cuore'))
theDonors.append((u'------- UzPEC',u'UzPEC'))
theDonors.append((u'United Nations',u'United Nations'))
theDonors.append((u'--- All',u'All'))
theDonors.append((u'--- FAO',u'FAO'))
theDonors.append((u'--- UN Habitat',u'UN Habitat'))
theDonors.append((u'--- UNDP / PNUD',u'UNDP / PNUD'))
theDonors.append((u'--- UNESCO',u'UNESCO'))
theDonors.append((u'--- UNHCR',u'UNHCR'))
theDonors.append((u'--- UNICEF',u'UNICEF'))
theDonors.append((u'--- UNOCHA',u'UNOCHA'))
theDonors.append((u'--- WFP / PAM',u'WFP / PAM'))
theDonors.append((u'--- WHO / OMS',u'WHO / OMS'))
theDonors.append((u'--- Other:',u'Other United Nations'))
theDonors.append((u'------- MINUSTAH',u'MINUSTAH'))
theDonors.append((u'------- MONUC',u'MONUC'))
theDonors.append((u'------- Pooled Fund',u'Pooled Fund'))
theDonors.append((u'------- UNAMA',u'UNAMA'))
theDonors.append((u'------- UNDEF',u'UNDEF'))
theDonors.append((u'------- UNFPA',u'UNFPA'))
theDonors.append((u'------- UNIFEM',u'UNIFEM'))
theDonors.append((u'------- UNMIK',u'UNMIK'))
theDonors.append((u'------- UNRWA',u'UNRWA'))







theSectors = (
'Culture & Heritage',
'Disaster Risk Reduction & Environment',
'Economic Development',
'Education & Training',
'Emergency',
'Food Security & Livelihood',
'Local Governance',
'Shelter & Infrastructure',
'WASH & Health',
'Other'
)


theCountries = (
'Afghanistan',
'Albania',
'Bangladesh',
'Cambodia',
'Central African Republic',
'Chad',
'Congo Brazzaville',
'Democratic Republic of Congo',
'Europe',
'Ethiopia',
'France',
'Haiti',
'India',
'Indonesia',
'Iraq',
'Jordan',
'Kosovo',
'Kenya',
'Kyrgyzstan',
'Lebanon',
'Libya',
'Macedonia',
'Myanmar',
'Nicaragua',
'Niger',
'Palestinan Occupied Territories',
'Pakistan',
'Republic of Congo',
'Serbia',
'Somalia',
'Sri Lanka',
'Sudan',
'Syria',
'Tajikistan',
'Uganda',
'Uzbekistan',
'Vietnam',
'Zimbabwe'
)



############################################################################

# note the encode to utf-8 here, this is the bug ivan fixed 12 Nov 2010
ACTED_DONORS = DisplayList()
for donor in theDonors:
   ACTED_DONORS.add(donor[1].encode("utf-8"),donor[0].encode("utf-8") )

ACTED_COUNTRIES = DisplayList()
for country in theCountries:
   ACTED_COUNTRIES.add(country,country)

ACTED_SECTORS = DisplayList()
for sector in theSectors:
   ACTED_SECTORS.add(sector,sector)

ACTED_YEARS = DisplayList()
for year in theYears:
   ACTED_YEARS.add(year,year)


PROJECTNAME = 'acted.projects'
ADD_PERMISSIONS = {
    'ACTEDProject': 'acted.projects: Add ACTED Project',
    'MyMut': 'acted.projects: Add ACTED Project',
}

