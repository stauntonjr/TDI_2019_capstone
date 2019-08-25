# bokeh_plot.py 
# run: bokeh serve bokeh_plot.py --args

# import modules
from collections import defaultdict
import numpy as np
from flask import Flask, render_template, render_template_string
import alpha_vantage
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import talib
from talib import abstract
from fred import Fred
from datetime import datetime
from bokeh.embed import server_document
import requests
from requests_futures.sessions import FuturesSession
import time
from io import BytesIO
from zipfile import ZipFile
import os
import gzip
import json
import pandas as pd
from pandas import Series

from bokeh.io import curdoc
from bokeh.server.server import Server
from bokeh.embed import server_document
from bokeh.models import (BoxSelectTool, ColumnDataSource, CDSView,
                        CategoricalColorMapper, NumeralTickFormatter, 
                        HoverTool, Button, CustomJS, GroupFilter)
from bokeh.models.ranges import Range1d
from bokeh.models.widgets import (Select, Button, Div, RadioGroup,
                                 TableColumn, DataTable)
from bokeh.models.annotations import BoxAnnotation
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.palettes import Spectral5, mpl, Spectral10, Spectral4
from bokeh.themes import Theme
from tornado.ioloop import IOLoop
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler

import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import pacf
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.distributions.empirical_distribution import ECDF

import pyramid as pm
from pyramid.arima import auto_arima
from pyramid.arima import arima as pyrima

from sklearn import base, tree
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import (RandomForestClassifier, AdaBoostClassifier, 
                            GradientBoostingClassifier, VotingClassifier)
from sklearn.feature_extraction import DictVectorizer
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.svm import SVC
from sklearn.utils import shuffle

AV_API_key = '567TRV8RTL728INO' # Alpha Vantage
ts = TimeSeries(key=AV_API_key)
fx = ForeignExchange(key=AV_API_key)
cc = CryptoCurrencies(key=AV_API_key)

FRED_API_Key = 'a615f729065fa8c55e2014da998b8bd9' #FRED

ticker_header = 'type, name, code'
ticker_string = """ Digital Currency,FirstBlood (1ST),1ST
                    Digital Currency,GiveCoin (2GIVE),2GIVE
                    Digital Currency,808Coin (808),808
                    Digital Currency,ArcBlock (ABT),ABT
                    Digital Currency,ArtByte (ABY),ABY
                    Digital Currency,AsiaCoin (AC),AC
                    Digital Currency,Achain (ACT),ACT
                    Digital Currency,Cardano (ADA),ADA
                    Digital Currency,adToken (ADT),ADT
                    Digital Currency,AdEx (ADX),ADX
                    Digital Currency,Aeternity (AE),AE
                    Digital Currency,Aeon (AEON),AEON
                    Digital Currency,SingularityNET (AGI),AGI
                    Digital Currency,IDNI-Agoras (AGRS),AGRS
                    Digital Currency,POLY-AI (AI),AI
                    Digital Currency,AidCoin (AID),AID
                    Digital Currency,Aion (AION),AION
                    Digital Currency,AirToken (AIR),AIR
                    Digital Currency,Akuya-Coin (AKY),AKY
                    Digital Currency,ALIS (ALIS),ALIS
                    Digital Currency,AmberCoin (AMBER),AMBER
                    Digital Currency,Synereo (AMP),AMP
                    Digital Currency,Anoncoin (ANC),ANC
                    Digital Currency,Aragon (ANT),ANT
                    Digital Currency,AppCoins (APPC),APPC
                    Digital Currency,APX-Ventures (APX),APX
                    Digital Currency,Ardor (ARDR),ARDR
                    Digital Currency,Ark (ARK),ARK
                    Digital Currency,Aeron (ARN),ARN
                    Digital Currency,AirSwap (AST),AST
                    Digital Currency,ATBCoin (ATB),ATB
                    Digital Currency,ATMChain (ATM),ATM
                    Digital Currency,Authorship (ATS),ATS
                    Digital Currency,Auroracoin (AUR),AUR
                    Digital Currency,Aventus (AVT),AVT
                    Digital Currency,B3Coin (B3),B3
                    Digital Currency,Basic-Attention-Token (BAT),BAT
                    Digital Currency,BitBay (BAY),BAY
                    Digital Currency,Boolberry (BBR),BBR
                    Digital Currency,BCAP (BCAP),BCAP
                    Digital Currency,BitConnect (BCC),BCC
                    Digital Currency,Bitcoin-Diamond (BCD),BCD
                    Digital Currency,Bitcoin-Cash (BCH),BCH
                    Digital Currency,Bytecoin (BCN),BCN
                    Digital Currency,BlockMason-Credit-Protocol-Token (BCPT),BCPT
                    Digital Currency,BitcoinX (BCX),BCX
                    Digital Currency,BitCrystals (BCY),BCY
                    Digital Currency,Bitdeal (BDL),BDL
                    Digital Currency,Bee-Token (BEE),BEE
                    Digital Currency,BelaCoin (BELA),BELA
                    Digital Currency,DAO-Casino (BET),BET
                    Digital Currency,BF-Token (BFT),BFT
                    Digital Currency,Bismuth (BIS),BIS
                    Digital Currency,BitBean (BITB),BITB
                    Digital Currency,BitBTC (BITBTC),BITBTC
                    Digital Currency,BitCNY (BITCNY),BITCNY
                    Digital Currency,BitEUR (BITEUR),BITEUR
                    Digital Currency,BitGOLD (BITGOLD),BITGOLD
                    Digital Currency,BitSILVER (BITSILVER),BITSILVER
                    Digital Currency,BitUSD (BITUSD),BITUSD
                    Digital Currency,Bibox-Token (BIX),BIX
                    Digital Currency,Blitzcash (BLITZ),BLITZ
                    Digital Currency,Blackcoin (BLK),BLK
                    Digital Currency,Bolenum (BLN),BLN
                    Digital Currency,Blocknet (BLOCK),BLOCK
                    Digital Currency,Bluzelle (BLZ),BLZ
                    Digital Currency,Blackmoon-Crypto (BMC),BMC
                    Digital Currency,Binance-Coin (BNB),BNB
                    Digital Currency,Bancor-Network-Token (BNT),BNT
                    Digital Currency,Bounty0x (BNTY),BNTY
                    Digital Currency,BoostCoin (BOST),BOST
                    Digital Currency,Bodhi (BOT),BOT
                    Digital Currency,bitqy (BQ),BQ
                    Digital Currency,Bread (BRD),BRD
                    Digital Currency,Breakout-Coin (BRK),BRK
                    Digital Currency,Breakout-Stake (BRX),BRX
                    Digital Currency,Bata (BTA),BTA
                    Digital Currency,Bitcoin (BTC),BTC
                    Digital Currency,BitcoinDark (BTCD),BTCD
                    Digital Currency,Bitcoin-Private (BTCP),BTCP
                    Digital Currency,Bitcoin-Gold (BTG),BTG
                    Digital Currency,Bitmark (BTM),BTM
                    Digital Currency,BitShares (BTS),BTS
                    Digital Currency,BTSR (BTSR),BTSR
                    Digital Currency,Bitcore (BTX),BTX
                    Digital Currency,Burstcoin (BURST),BURST
                    Digital Currency,BuzzCoin (BUZZ),BUZZ
                    Digital Currency,Bytecent (BYC),BYC
                    Digital Currency,Bytom (BYTOM),BYTOM
                    Digital Currency,Crypto20 (C20),C20
                    Digital Currency,CannabisCoin (CANN),CANN
                    Digital Currency,BlockCAT (CAT),CAT
                    Digital Currency,CryptoCarbon (CCRB),CCRB
                    Digital Currency,Blox (CDT),CDT
                    Digital Currency,Cofound-it (CFI),CFI
                    Digital Currency,ChatCoin (CHAT),CHAT
                    Digital Currency,Chips (CHIPS),CHIPS
                    Digital Currency,Clams (CLAM),CLAM
                    Digital Currency,CloakCoin (CLOAK),CLOAK
                    Digital Currency,Compcoin (CMP),CMP
                    Digital Currency,CyberMiles (CMT),CMT
                    Digital Currency,Cindicator (CND),CND
                    Digital Currency,Cryptonex (CNX),CNX
                    Digital Currency,CoinFi (COFI),COFI
                    Digital Currency,COSS (COSS),COSS
                    Digital Currency,Circuits-Of-Value (COVAL),COVAL
                    Digital Currency,CreditBIT (CRBIT),CRBIT
                    Digital Currency,CreativeCoin (CREA),CREA
                    Digital Currency,Credo (CREDO),CREDO
                    Digital Currency,Crown (CRW),CRW
                    Digital Currency,BitDice (CSNO),CSNO
                    Digital Currency,Centra (CTR),CTR
                    Digital Currency,Cortex (CTXC),CTXC
                    Digital Currency,CureCoin (CURE),CURE
                    Digital Currency,Civic (CVC),CVC
                    Digital Currency,Dai (DAI),DAI
                    Digital Currency,Darcrus (DAR),DAR
                    Digital Currency,Dash (DASH),DASH
                    Digital Currency,DATAcoin (DATA),DATA
                    Digital Currency,Chronologic (DAY),DAY
                    Digital Currency,DeepBrain-Chain (DBC),DBC
                    Digital Currency,DubaiCoin (DBIX),DBIX
                    Digital Currency,Dentacoin (DCN),DCN
                    Digital Currency,Decred (DCR),DCR
                    Digital Currency,DECENT (DCT),DCT
                    Digital Currency,Digital-Developers-Fund (DDF),DDF
                    Digital Currency,Dent (DENT),DENT
                    Digital Currency,DFSCoin (DFS),DFS
                    Digital Currency,DigiByte (DGB),DGB
                    Digital Currency,Digitalcoin (DGC),DGC
                    Digital Currency,DigixDAO (DGD),DGD
                    Digital Currency,Etheroll (DICE),DICE
                    Digital Currency,Agrello-Delta (DLT),DLT
                    Digital Currency,Diamond (DMD),DMD
                    Digital Currency,DMarket (DMT),DMT
                    Digital Currency,district0x (DNT),DNT
                    Digital Currency,DogeCoin (DOGE),DOGE
                    Digital Currency,DopeCoin (DOPE),DOPE
                    Digital Currency,Dragonchain (DRGN),DRGN
                    Digital Currency,Data (DTA),DTA
                    Digital Currency,Databits (DTB),DTB
                    Digital Currency,Dynamic (DYN),DYN
                    Digital Currency,EarthCoin (EAC),EAC
                    Digital Currency,eBoost (EBST),EBST
                    Digital Currency,eBTC (EBTC),EBTC
                    Digital Currency,ECC (ECC),ECC
                    Digital Currency,E-coin (ECN),ECN
                    Digital Currency,Edgeless (EDG),EDG
                    Digital Currency,Eidoo (EDO),EDO
                    Digital Currency,Electronic-Gulden (EFL),EFL
                    Digital Currency,EverGreenCoin (EGC),EGC
                    Digital Currency,EDUCare (EKT),EKT
                    Digital Currency,Elastos (ELA),ELA
                    Digital Currency,Electrify.Asia (ELEC),ELEC
                    Digital Currency,aelf (ELF),ELF
                    Digital Currency,Elixir (ELIX),ELIX
                    Digital Currency,Embercoin (EMB),EMB
                    Digital Currency,Emercoin (EMC),EMC
                    Digital Currency,Einsteinium (EMC2),EMC2
                    Digital Currency,Enigma (ENG),ENG
                    Digital Currency,Enjin-Coin (ENJ),ENJ
                    Digital Currency,EnergyCoin (ENRG),ENRG
                    Digital Currency,EOS (EOS),EOS
                    Digital Currency,EOT-Token (EOT),EOT
                    Digital Currency,EquiTrader (EQT),EQT
                    Digital Currency,EuropeCoin (ERC),ERC
                    Digital Currency,Ethereum-Classic (ETC),ETC
                    Digital Currency,Ethereum (ETH),ETH
                    Digital Currency,Ethereum-Dark (ETHD),ETHD
                    Digital Currency,Ethos (ETHOS),ETHOS
                    Digital Currency,Electroneum (ETN),ETN
                    Digital Currency,Metaverse-Entropy (ETP),ETP
                    Digital Currency,EncryptoTel (ETT),ETT
                    Digital Currency,Devery (EVE),EVE
                    Digital Currency,Everex (EVX),EVX
                    Digital Currency,ExclusiveCoin (EXCL),EXCL
                    Digital Currency,Expanse (EXP),EXP
                    Digital Currency,Factom (FCT),FCT
                    Digital Currency,FoldingCoin (FLDC),FLDC
                    Digital Currency,FlorinCoin (FLO),FLO
                    Digital Currency,FlutterCoin (FLT),FLT
                    Digital Currency,FirstCoin (FRST),FRST
                    Digital Currency,Feathercoin (FTC),FTC
                    Digital Currency,Etherparty (FUEL),FUEL
                    Digital Currency,FunFair (FUN),FUN
                    Digital Currency,Gambit (GAM),GAM
                    Digital Currency,GameCredits (GAME),GAME
                    Digital Currency,Gas (GAS),GAS
                    Digital Currency,Golos Gold (GBG),GBG
                    Digital Currency,GoByte (GBX),GBX
                    Digital Currency,Byteball (GBYTE),GBYTE
                    Digital Currency,GCRCoin (GCR),GCR
                    Digital Currency,GeoCoin (GEO),GEO
                    Digital Currency,GoldCoin (GLD),GLD
                    Digital Currency,Gnosis-Token (GNO),GNO
                    Digital Currency,Golem-Tokens (GNT),GNT
                    Digital Currency,Golos (GOLOS),GOLOS
                    Digital Currency,Gridcoin (GRC),GRC
                    Digital Currency,Groestlcoin (GRS),GRS
                    Digital Currency,Growers-International (GRWI),GRWI
                    Digital Currency,Game (GTC),GTC
                    Digital Currency,Gifto (GTO),GTO
                    Digital Currency,Guppy (GUP),GUP
                    Digital Currency,Genesis-Vision (GVT),GVT
                    Digital Currency,GXShares (GXS),GXS
                    Digital Currency,HoboNickels (HBN),HBN
                    Digital Currency,HEAT (HEAT),HEAT
                    Digital Currency,Humaniq (HMQ),HMQ
                    Digital Currency,High-Performance-Blockchain (HPB),HPB
                    Digital Currency,Hshare (HSR),HSR
                    Digital Currency,Hush (HUSH),HUSH
                    Digital Currency,Hive (HVN),HVN
                    Digital Currency,HexxCoin (HXX),HXX
                    Digital Currency,ICONOMI (ICN),ICN
                    Digital Currency,ICON (ICX),ICX
                    Digital Currency,Infinitecoin (IFC),IFC
                    Digital Currency,investFeed (IFT),IFT
                    Digital Currency,Ignis (IGNIS),IGNIS
                    Digital Currency,Incent (INCNT),INCNT
                    Digital Currency,Indorse-Token (IND),IND
                    Digital Currency,InfChain (INF),INF
                    Digital Currency,Ink (INK),INK
                    Digital Currency,INS-Ecosystem (INS),INS
                    Digital Currency,Insights-Network (INSTAR),INSTAR
                    Digital Currency,Internet-Node-Token (INT),INT
                    Digital Currency,Internxt (INXT),INXT
                    Digital Currency,IOCoin (IOC),IOC
                    Digital Currency,ION (ION),ION
                    Digital Currency,Internet-of-People (IOP),IOP
                    Digital Currency,IOStoken (IOST),IOST
                    Digital Currency,IOTA (IOTA),IOTA
                    Digital Currency,IoTeX (IOTX),IOTX
                    Digital Currency,Iquant-Chain (IQT),IQT
                    Digital Currency,IoT-Chain (ITC),ITC
                    Digital Currency,iXcoin (IXC),IXC
                    Digital Currency,InsureX (IXT),IXT
                    Digital Currency,JET8 (J8T),J8T
                    Digital Currency,Jibrel-Network (JNT),JNT
                    Digital Currency,KuCoin (KCS),KCS
                    Digital Currency,KickCoin (KICK),KICK
                    Digital Currency,KIN (KIN),KIN
                    Digital Currency,Komodo (KMD),KMD
                    Digital Currency,Kyber-Network (KNC),KNC
                    Digital Currency,KoreCoin (KORE),KORE
                    Digital Currency,LBRY-Credits (LBC),LBC
                    Digital Currency,Litecoin-Cash (LCC),LCC
                    Digital Currency,EthLend (LEND),LEND
                    Digital Currency,Leverj (LEV),LEV
                    Digital Currency,Legends-Room (LGD),LGD
                    Digital Currency,Linda (LINDA),LINDA
                    Digital Currency,ChainLink (LINK),LINK
                    Digital Currency,Lykke (LKK),LKK
                    Digital Currency,LoMoCoin (LMC),LMC
                    Digital Currency,LOCIcoin (LOCI),LOCI
                    Digital Currency,Loom-Token (LOOM),LOOM
                    Digital Currency,Loopring (LRC),LRC
                    Digital Currency,Lisk (LSK),LSK
                    Digital Currency,Litecoin (LTC),LTC
                    Digital Currency,Lunyr (LUN),LUN
                    Digital Currency,MaidSafeCoin (MAID),MAID
                    Digital Currency,Decentraland (MANA),MANA
                    Digital Currency,Maxcoin (MAX),MAX
                    Digital Currency,Embers (MBRS),MBRS
                    Digital Currency,MCAP (MCAP),MCAP
                    Digital Currency,Monaco (MCO),MCO
                    Digital Currency,Moeda-Loyalty-Points (MDA),MDA
                    Digital Currency,Megacoin (MEC),MEC
                    Digital Currency,MediBlock (MED),MED
                    Digital Currency,Memetic (MEME),MEME
                    Digital Currency,Mercury (MER),MER
                    Digital Currency,MergeCoin (MGC),MGC
                    Digital Currency,MobileGo (MGO),MGO
                    Digital Currency,Minex (MINEX),MINEX
                    Digital Currency,Mintcoin (MINT),MINT
                    Digital Currency,Mithril (MITH),MITH
                    Digital Currency,Maker (MKR),MKR
                    Digital Currency,Melon (MLN),MLN
                    Digital Currency,Minereum (MNE),MNE
                    Digital Currency,MinexCoin (MNX),MNX
                    Digital Currency,Modum (MOD),MOD
                    Digital Currency,MonaCoin (MONA),MONA
                    Digital Currency,Miners-Reward-Token (MRT),MRT
                    Digital Currency,Mothership (MSP),MSP
                    Digital Currency,Monetha (MTH),MTH
                    Digital Currency,MedToken (MTN),MTN
                    Digital Currency,MonetaryUnit (MUE),MUE
                    Digital Currency,Musicoin (MUSIC),MUSIC
                    Digital Currency,MyBit-Token (MYB),MYB
                    Digital Currency,Mysterium (MYST),MYST
                    Digital Currency,Mazacoin (MZC),MZC
                    Digital Currency,Namocoin (NAMO),NAMO
                    Digital Currency,Nano (NANO),NANO
                    Digital Currency,Nebulas-Token (NAS),NAS
                    Digital Currency,Nav-Coin (NAV),NAV
                    Digital Currency,NuBits (NBT),NBT
                    Digital Currency,Nucleus-Vision (NCASH),NCASH
                    Digital Currency,NeverDie-Coin (NDC),NDC
                    Digital Currency,Neblio (NEBL),NEBL
                    Digital Currency,NEO (NEO),NEO
                    Digital Currency,NeosCoin (NEOS),NEOS
                    Digital Currency,Nimiq (NET),NET
                    Digital Currency,NoLimitCoin (NLC2),NLC2
                    Digital Currency,Gulden (NLG),NLG
                    Digital Currency,Namecoin (NMC),NMC
                    Digital Currency,Numeraire (NMR),NMR
                    Digital Currency,NobleCoin (NOBL),NOBL
                    Digital Currency,DNotes (NOTE),NOTE
                    Digital Currency,Pundi-X-Token (NPXS),NPXS
                    Digital Currency,NuShares (NSR),NSR
                    Digital Currency,Fujinto (NTO),NTO
                    Digital Currency,Nuls (NULS),NULS
                    Digital Currency,Novacoin (NVC),NVC
                    Digital Currency,Nexium (NXC),NXC
                    Digital Currency,Nexus (NXS),NXS
                    Digital Currency,Nxt (NXT),NXT
                    Digital Currency,openANX (OAX),OAX
                    Digital Currency,Obits (OBITS),OBITS
                    Digital Currency,Oceanlab (OCL),OCL
                    Digital Currency,Odyssey (OCN),OCN
                    Digital Currency,ODEM (ODEM),ODEM
                    Digital Currency,Obsidian (ODN),ODN
                    Digital Currency,OFCOIN (OF),OF
                    Digital Currency,OKCash (OK),OK
                    Digital Currency,OmiseGo (OMG),OMG
                    Digital Currency,Omni (OMNI),OMNI
                    Digital Currency,DeepOnion (ONION),ONION
                    Digital Currency,Ontology (ONT),ONT
                    Digital Currency,Opus (OPT),OPT
                    Digital Currency,Simple-Token (OST),OST
                    Digital Currency,Particl (PART),PART
                    Digital Currency,PascalCoin (PASC),PASC
                    Digital Currency,TenX (PAY),PAY
                    Digital Currency,Pebbles (PBL),PBL
                    Digital Currency,Primalbase-Token (PBT),PBT
                    Digital Currency,Payfair (PFR),PFR
                    Digital Currency,CryptoPing (PING),PING
                    Digital Currency,Pinkcoin (PINK),PINK
                    Digital Currency,PIVX (PIVX),PIVX
                    Digital Currency,Lampix (PIX),PIX
                    Digital Currency,Polybius (PLBT),PLBT
                    Digital Currency,Pillar (PLR),PLR
                    Digital Currency,Pluton (PLU),PLU
                    Digital Currency,POA-Network (POA),POA
                    Digital Currency,Poet (POE),POE
                    Digital Currency,Polymath (POLY),POLY
                    Digital Currency,PoSW-Coin (POSW),POSW
                    Digital Currency,PotCoin (POT),POT
                    Digital Currency,Power-Ledger (POWR),POWR
                    Digital Currency,Peercoin (PPC),PPC
                    Digital Currency,Populous (PPT),PPT
                    Digital Currency,Peerplays (PPY),PPY
                    Digital Currency,Paragon-Coin (PRG),PRG
                    Digital Currency,Oyster-Pearl (PRL),PRL
                    Digital Currency,Propy (PRO),PRO
                    Digital Currency,Primas (PST),PST
                    Digital Currency,Pesetacoin (PTC),PTC
                    Digital Currency,Patientory (PTOY),PTOY
                    Digital Currency,Pura (PURA),PURA
                    Digital Currency,QASH (QASH),QASH
                    Digital Currency,Quantum (QAU),QAU
                    Digital Currency,Qlink (QLC),QLC
                    Digital Currency,Quark (QRK),QRK
                    Digital Currency,Quantum-Resistant-Ledger (QRL),QRL
                    Digital Currency,Quantstamp (QSP),QSP
                    Digital Currency,Quatloo (QTL),QTL
                    Digital Currency,Qtum (QTUM),QTUM
                    Digital Currency,Qwark (QWARK),QWARK
                    Digital Currency,Revain (R),R
                    Digital Currency,Radium (RADS),RADS
                    Digital Currency,Condensate (RAIN),RAIN
                    Digital Currency,Rubies (RBIES),RBIES
                    Digital Currency,Ripto-Bux (RBX),RBX
                    Digital Currency,RubyCoin (RBY),RBY
                    Digital Currency,Ripio-Credit-Network (RCN),RCN
                    Digital Currency,ReddCoin (RDD),RDD
                    Digital Currency,Raiden-Network-Token (RDN),RDN
                    Digital Currency,Regalcoin (REC),REC
                    Digital Currency,Redcoin (RED),RED
                    Digital Currency,Augur (REP),REP
                    Digital Currency,Request-Network (REQ),REQ
                    Digital Currency,RChain (RHOC),RHOC
                    Digital Currency,Riecoin (RIC),RIC
                    Digital Currency,Rise (RISE),RISE
                    Digital Currency,RLC-Token (RLC),RLC
                    Digital Currency,RouletteToken (RLT),RLT
                    Digital Currency,Red-Pulse (RPX),RPX
                    Digital Currency,Recovery-Right-Tokens (RRT),RRT
                    Digital Currency,Ruff (RUFF),RUFF
                    Digital Currency,Rupee (RUP),RUP
                    Digital Currency,Rivetz (RVT),RVT
                    Digital Currency,SafeExchangeCoin (SAFEX),SAFEX
                    Digital Currency,Salt (SALT),SALT
                    Digital Currency,Santiment-Network-Token (SAN),SAN
                    Digital Currency,Steem-Dollars (SBD),SBD
                    Digital Currency,Super-Bitcoin (SBTC),SBTC
                    Digital Currency,Siacoin (SC),SC
                    Digital Currency,Seele (SEELE),SEELE
                    Digital Currency,Sequence (SEQ),SEQ
                    Digital Currency,SHIFT (SHIFT),SHIFT
                    Digital Currency,SIBCoin (SIB),SIB
                    Digital Currency,SIGMAcoin (SIGMA),SIGMA
                    Digital Currency,Signatum (SIGT),SIGT
                    Digital Currency,Storjcoin-X (SJCX),SJCX
                    Digital Currency,SkinCoin (SKIN),SKIN
                    Digital Currency,Skycoin (SKY),SKY
                    Digital Currency,SolarCoin (SLR),SLR
                    Digital Currency,SaluS (SLS),SLS
                    Digital Currency,SmartCash (SMART),SMART
                    Digital Currency,SmartMesh (SMT),SMT
                    Digital Currency,SunContract (SNC),SNC
                    Digital Currency,SingularDTV (SNGLS),SNGLS
                    Digital Currency,SONM (SNM),SNM
                    Digital Currency,Synergy (SNRG),SNRG
                    Digital Currency,Status-Network-Token (SNT),SNT
                    Digital Currency,All-Sports (SOC),SOC
                    Digital Currency,Phantasma (SOUL),SOUL
                    Digital Currency,SpankChain (SPANK),SPANK
                    Digital Currency,SpaceChain (SPC),SPC
                    Digital Currency,Sphere (SPHR),SPHR
                    Digital Currency,SpreadCoin (SPR),SPR
                    Digital Currency,Sirin-Labs-Token (SRN),SRN
                    Digital Currency,Startcoin (START),START
                    Digital Currency,Steem (STEEM),STEEM
                    Digital Currency,STK-Token (STK),STK
                    Digital Currency,Storj (STORJ),STORJ
                    Digital Currency,Storm (STORM),STORM
                    Digital Currency,Storiqa (STQ),STQ
                    Digital Currency,Stratis (STRAT),STRAT
                    Digital Currency,Stox (STX),STX
                    Digital Currency,Substratum (SUB),SUB
                    Digital Currency,SwftCoin (SWFTC),SWFTC
                    Digital Currency,Bitswift (SWIFT),SWIFT
                    Digital Currency,Swarm-City (SWT),SWT
                    Digital Currency,Syndicate (SYNX),SYNX
                    Digital Currency,SysCoin (SYS),SYS
                    Digital Currency,Taas (TAAS),TAAS
                    Digital Currency,Lamden (TAU),TAU
                    Digital Currency,The-ChampCoin (TCC),TCC
                    Digital Currency,True-Flip (TFL),TFL
                    Digital Currency,HempCoin (THC),THC
                    Digital Currency,Theta-Token (THETA),THETA
                    Digital Currency,Time (TIME),TIME
                    Digital Currency,Blocktix (TIX),TIX
                    Digital Currency,TokenCard (TKN),TKN
                    Digital Currency,Trackr (TKR),TKR
                    Digital Currency,Tokes (TKS),TKS
                    Digital Currency,Time-New-Bank (TNB),TNB
                    Digital Currency,Tierion (TNT),TNT
                    Digital Currency,ToaCoin (TOA),TOA
                    Digital Currency,OriginTrail (TRAC),TRAC
                    Digital Currency,Terracoin (TRC),TRC
                    Digital Currency,Tracto (TRCT),TRCT
                    Digital Currency,Triggers (TRIG),TRIG
                    Digital Currency,Trustcoin (TRST),TRST
                    Digital Currency,TrueChain (TRUE),TRUE
                    Digital Currency,TrustPlus (TRUST),TRUST
                    Digital Currency,Tronix (TRX),TRX
                    Digital Currency,TrueUSD (TUSD),TUSD
                    Digital Currency,TransferCoin (TX),TX
                    Digital Currency,Ubiq (UBQ),UBQ
                    Digital Currency,UnikoinGold (UKG),UKG
                    Digital Currency,Ulatech (ULA),ULA
                    Digital Currency,UnbreakableCoin (UNB),UNB
                    Digital Currency,SuperNET (UNITY),UNITY
                    Digital Currency,Unobtanium (UNO),UNO
                    Digital Currency,Unity-Ingot (UNY),UNY
                    Digital Currency,UpToken (UP),UP
                    Digital Currency,Uro (URO),URO
                    Digital Currency,Tether (USDT),USDT
                    Digital Currency,UTrust (UTK),UTK
                    Digital Currency,BLOCKv (VEE),VEE
                    Digital Currency,VeChain (VEN),VEN
                    Digital Currency,Veritaseum (VERI),VERI
                    Digital Currency,Viacoin (VIA),VIA
                    Digital Currency,Viberate (VIB),VIB
                    Digital Currency,Vibe (VIBE),VIBE
                    Digital Currency,VIVO (VIVO),VIVO
                    Digital Currency,Voise (VOISE),VOISE
                    Digital Currency,Voxels (VOX),VOX
                    Digital Currency,VPNCoin (VPN),VPN
                    Digital Currency,Vericoin (VRC),VRC
                    Digital Currency,Verium (VRM),VRM
                    Digital Currency,Veros (VRS),VRS
                    Digital Currency,vSlice (VSL),VSL
                    Digital Currency,Vertcoin (VTC),VTC
                    Digital Currency,vTorrent (VTR),VTR
                    Digital Currency,WaBi (WABI),WABI
                    Digital Currency,Wanchain (WAN),WAN
                    Digital Currency,Waves (WAVES),WAVES
                    Digital Currency,Wax-Token (WAX),WAX
                    Digital Currency,Waves-Community (WCT),WCT
                    Digital Currency,WorldCoin (WDC),WDC
                    Digital Currency,WavesGo (WGO),WGO
                    Digital Currency,Wagerr (WGR),WGR
                    Digital Currency,Wings (WINGS),WINGS
                    Digital Currency,WePower (WPR),WPR
                    Digital Currency,Walton (WTC),WTC
                    Digital Currency,Giga-Watt-Token (WTT),WTT
                    Digital Currency,Asch (XAS),XAS
                    Digital Currency,Xaurum (XAUR),XAUR
                    Digital Currency,Bitcoin-Plus (XBC),XBC
                    Digital Currency,XtraBYtes (XBY),XBY
                    Digital Currency,Cryptonite (XCN),XCN
                    Digital Currency,Counterparty (XCP),XCP
                    Digital Currency,DigitalNote (XDN),XDN
                    Digital Currency,Elastic (XEL),XEL
                    Digital Currency,NEM (XEM),XEM
                    Digital Currency,Sphere-Identity (XID),XID
                    Digital Currency,Stellar (XLM),XLM
                    Digital Currency,Magi (XMG),XMG
                    Digital Currency,Monero (XMR),XMR
                    Digital Currency,Metal (XMT),XMT
                    Digital Currency,Myriadcoin (XMY),XMY
                    Digital Currency,Primecoin (XPM),XPM
                    Digital Currency,Rialto (XRL),XRL
                    Digital Currency,Ripple (XRP),XRP
                    Digital Currency,Spectrecoin (XSPEC),XSPEC
                    Digital Currency,Stealthcoin (XST),XST
                    Digital Currency,Tezos (XTZ),XTZ
                    Digital Currency,Exchange-Union (XUC),XUC
                    Digital Currency,Vcash (XVC),XVC
                    Digital Currency,Verge (XVG),XVG
                    Digital Currency,WhiteCoin (XWC),XWC
                    Digital Currency,ZCoin (XZC),XZC
                    Digital Currency,ZrCoin (XZR),XZR
                    Digital Currency,Yee (YEE),YEE
                    Digital Currency,YOYOW (YOYOW),YOYOW
                    Digital Currency,ZcCoin (ZCC),ZCC
                    Digital Currency,Zclassic (ZCL),ZCL
                    Digital Currency,Zebi (ZCO),ZCO
                    Digital Currency,Zcash (ZEC),ZEC
                    Digital Currency,ZenCash (ZEN),ZEN
                    Digital Currency,Zetacoin (ZET),ZET
                    Digital Currency,Zilliqa (ZIL),ZIL
                    Digital Currency,Zilla (ZLA),ZLA
                    Digital Currency,0x (ZRX),ZRX
                    Physical Currency,United Arab Emirates Dirham (AED),AED
                    Physical Currency,Afghan Afghani (AFN),AFN
                    Physical Currency,Albanian Lek (ALL),ALL
                    Physical Currency,Armenian Dram (AMD),AMD
                    Physical Currency,Netherlands Antillean Guilder (ANG),ANG
                    Physical Currency,Angolan Kwanza (AOA),AOA
                    Physical Currency,Argentine Peso (ARS),ARS
                    Physical Currency,Australian Dollar (AUD),AUD
                    Physical Currency,Aruban Florin (AWG),AWG
                    Physical Currency,Azerbaijani Manat (AZN),AZN
                    Physical Currency,Bosnia-Herzegovina Convertible Mark (BAM),BAM
                    Physical Currency,Barbadian Dollar (BBD),BBD
                    Physical Currency,Bangladeshi Taka (BDT),BDT
                    Physical Currency,Bulgarian Lev (BGN),BGN
                    Physical Currency,Bahraini Dinar (BHD),BHD
                    Physical Currency,Burundian Franc (BIF),BIF
                    Physical Currency,Bermudan Dollar (BMD),BMD
                    Physical Currency,Brunei Dollar (BND),BND
                    Physical Currency,Bolivian Boliviano (BOB),BOB
                    Physical Currency,Brazilian Real (BRL),BRL
                    Physical Currency,Bahamian Dollar (BSD),BSD
                    Physical Currency,Bhutanese Ngultrum (BTN),BTN
                    Physical Currency,Botswanan Pula (BWP),BWP
                    Physical Currency,Belize Dollar (BZD),BZD
                    Physical Currency,Canadian Dollar (CAD),CAD
                    Physical Currency,Congolese Franc (CDF),CDF
                    Physical Currency,Swiss Franc (CHF),CHF
                    Physical Currency,Chilean Unit of Account UF (CLF),CLF
                    Physical Currency,Chilean Peso (CLP),CLP
                    Physical Currency,Chinese Yuan Offshore (CNH),CNH
                    Physical Currency,Chinese Yuan (CNY),CNY
                    Physical Currency,Colombian Peso (COP),COP
                    Physical Currency,Cuban Peso (CUP),CUP
                    Physical Currency,Cape Verdean Escudo (CVE),CVE
                    Physical Currency,Czech Republic Koruna (CZK),CZK
                    Physical Currency,Djiboutian Franc (DJF),DJF
                    Physical Currency,Danish Krone (DKK),DKK
                    Physical Currency,Dominican Peso (DOP),DOP
                    Physical Currency,Algerian Dinar (DZD),DZD
                    Physical Currency,Egyptian Pound (EGP),EGP
                    Physical Currency,Eritrean Nakfa (ERN),ERN
                    Physical Currency,Ethiopian Birr (ETB),ETB
                    Physical Currency,Euro (EUR),EUR
                    Physical Currency,Fijian Dollar (FJD),FJD
                    Physical Currency,Falkland Islands Pound (FKP),FKP
                    Physical Currency,British Pound Sterling (GBP),GBP
                    Physical Currency,Georgian Lari (GEL),GEL
                    Physical Currency,Ghanaian Cedi (GHS),GHS
                    Physical Currency,Gibraltar Pound (GIP),GIP
                    Physical Currency,Gambian Dalasi (GMD),GMD
                    Physical Currency,Guinean Franc (GNF),GNF
                    Physical Currency,Guatemalan Quetzal (GTQ),GTQ
                    Physical Currency,Guyanaese Dollar (GYD),GYD
                    Physical Currency,Hong Kong Dollar (HKD),HKD
                    Physical Currency,Honduran Lempira (HNL),HNL
                    Physical Currency,Croatian Kuna (HRK),HRK
                    Physical Currency,Haitian Gourde (HTG),HTG
                    Physical Currency,Hungarian Forint (HUF),HUF
                    Physical Currency,Indonesian Rupiah (IDR),IDR
                    Physical Currency,Israeli New Sheqel (ILS),ILS
                    Physical Currency,Indian Rupee (INR),INR
                    Physical Currency,Iraqi Dinar (IQD),IQD
                    Physical Currency,Iranian Rial (IRR),IRR
                    Physical Currency,Icelandic Krona (ISK),ISK
                    Physical Currency,Jersey Pound (JEP),JEP
                    Physical Currency,Jamaican Dollar (JMD),JMD
                    Physical Currency,Jordanian Dinar (JOD),JOD
                    Physical Currency,Japanese Yen (JPY),JPY
                    Physical Currency,Kenyan Shilling (KES),KES
                    Physical Currency,Kyrgystani Som (KGS),KGS
                    Physical Currency,Cambodian Riel (KHR),KHR
                    Physical Currency,Comorian Franc (KMF),KMF
                    Physical Currency,North Korean Won (KPW),KPW
                    Physical Currency,South Korean Won (KRW),KRW
                    Physical Currency,Kuwaiti Dinar (KWD),KWD
                    Physical Currency,Cayman Islands Dollar (KYD),KYD
                    Physical Currency,Kazakhstani Tenge (KZT),KZT
                    Physical Currency,Laotian Kip (LAK),LAK
                    Physical Currency,Lebanese Pound (LBP),LBP
                    Physical Currency,Sri Lankan Rupee (LKR),LKR
                    Physical Currency,Liberian Dollar (LRD),LRD
                    Physical Currency,Lesotho Loti (LSL),LSL
                    Physical Currency,Libyan Dinar (LYD),LYD
                    Physical Currency,Moroccan Dirham (MAD),MAD
                    Physical Currency,Moldovan Leu (MDL),MDL
                    Physical Currency,Malagasy Ariary (MGA),MGA
                    Physical Currency,Macedonian Denar (MKD),MKD
                    Physical Currency,Myanma Kyat (MMK),MMK
                    Physical Currency,Mongolian Tugrik (MNT),MNT
                    Physical Currency,Macanese Pataca (MOP),MOP
                    Physical Currency,Mauritanian Ouguiya (pre-2018) (MRO),MRO
                    Physical Currency,Mauritanian Ouguiya (MRU),MRU
                    Physical Currency,Mauritian Rupee (MUR),MUR
                    Physical Currency,Maldivian Rufiyaa (MVR),MVR
                    Physical Currency,Malawian Kwacha (MWK),MWK
                    Physical Currency,Mexican Peso (MXN),MXN
                    Physical Currency,Malaysian Ringgit (MYR),MYR
                    Physical Currency,Mozambican Metical (MZN),MZN
                    Physical Currency,Namibian Dollar (NAD),NAD
                    Physical Currency,Nigerian Naira (NGN),NGN
                    Physical Currency,Norwegian Krone (NOK),NOK
                    Physical Currency,Nepalese Rupee (NPR),NPR
                    Physical Currency,New Zealand Dollar (NZD),NZD
                    Physical Currency,Omani Rial (OMR),OMR
                    Physical Currency,Panamanian Balboa (PAB),PAB
                    Physical Currency,Peruvian Nuevo Sol (PEN),PEN
                    Physical Currency,Papua New Guinean Kina (PGK),PGK
                    Physical Currency,Philippine Peso (PHP),PHP
                    Physical Currency,Pakistani Rupee (PKR),PKR
                    Physical Currency,Polish Zloty (PLN),PLN
                    Physical Currency,Paraguayan Guarani (PYG),PYG
                    Physical Currency,Qatari Rial (QAR),QAR
                    Physical Currency,Romanian Leu (RON),RON
                    Physical Currency,Serbian Dinar (RSD),RSD
                    Physical Currency,Russian Ruble (RUB),RUB
                    Physical Currency,Old Russian Ruble (RUR),RUR
                    Physical Currency,Rwandan Franc (RWF),RWF
                    Physical Currency,Saudi Riyal (SAR),SAR
                    Physical Currency,Solomon Islands Dollar (SBDf),SBDf
                    Physical Currency,Seychellois Rupee (SCR),SCR
                    Physical Currency,Sudanese Pound (SDG),SDG
                    Physical Currency,Swedish Krona (SEK),SEK
                    Physical Currency,Singapore Dollar (SGD),SGD
                    Physical Currency,Saint Helena Pound (SHP),SHP
                    Physical Currency,Sierra Leonean Leone (SLL),SLL
                    Physical Currency,Somali Shilling (SOS),SOS
                    Physical Currency,Surinamese Dollar (SRD),SRD
                    Physical Currency,Syrian Pound (SYP),SYP
                    Physical Currency,Swazi Lilangeni (SZL),SZL
                    Physical Currency,Thai Baht (THB),THB
                    Physical Currency,Tajikistani Somoni (TJS),TJS
                    Physical Currency,Turkmenistani Manat (TMT),TMT
                    Physical Currency,Tunisian Dinar (TND),TND
                    Physical Currency,Tongan Pa'anga (TOP),TOP
                    Physical Currency,Turkish Lira (TRY),TRY
                    Physical Currency,Trinidad and Tobago Dollar (TTD),TTD
                    Physical Currency,New Taiwan Dollar (TWD),TWD
                    Physical Currency,Tanzanian Shilling (TZS),TZS
                    Physical Currency,Ukrainian Hryvnia (UAH),UAH
                    Physical Currency,Ugandan Shilling (UGX),UGX
                    Physical Currency,United States Dollar (USD),USD
                    Physical Currency,Uruguayan Peso (UYU),UYU
                    Physical Currency,Uzbekistan Som (UZS),UZS
                    Physical Currency,Vietnamese Dong (VND),VND
                    Physical Currency,Vanuatu Vatu (VUV),VUV
                    Physical Currency,Samoan Tala (WST),WST
                    Physical Currency,CFA Franc BEAC (XAF),XAF
                    Physical Currency,Silver Ounce (XAG),XAG
                    Physical Currency,Gold Ounce (XAU),XAU
                    Physical Currency,East Caribbean Dollar (XCD),XCD
                    Physical Currency,Special Drawing Rights (XDR),XDR
                    Physical Currency,CFA Franc BCEAO (XOF),XOF
                    Physical Currency,CFP Franc (XPF),XPF
                    Physical Currency,Yemeni Rial (YER),YER
                    Physical Currency,South African Rand (ZAR),ZAR
                    Physical Currency,Zambian Kwacha (ZMW),ZMW
                    Physical Currency,Zimbabwean Dollar (ZWL),ZWL
                    AMEX Equity,"22nd Century Group, Inc (XXII)",XXII
                    AMEX Equity,Aberdeen Asia-Pacific Income Fund Inc (FAX),FAX
                    AMEX Equity,Aberdeen Australia Equity Fund Inc (IAF),IAF
                    AMEX Equity,"Aberdeen Emerging Markets Equity Income Fund, Inc. (AEF)",AEF
                    AMEX Equity,"Aberdeen Global Income Fund, Inc. (FCO)",FCO
                    AMEX Equity,Acme United Corporation. (ACU),ACU
                    AMEX Equity,"Actinium Pharmaceuticals, Inc. (ATNM)",ATNM
                    AMEX Equity,"Adams Resources & Energy, Inc. (AE)",AE
                    AMEX Equity,AeroCentury Corp. (ACY),ACY
                    AMEX Equity,"AgEagle Aerial Systems, Inc. (UAVS)",UAVS
                    AMEX Equity,"AgeX Therapeutics, Inc. (AGE)",AGE
                    AMEX Equity,Air Industries Group (AIRI),AIRI
                    AMEX Equity,Alexco Resource Corp (AXU),AXU
                    AMEX Equity,Alio Gold Inc. (ALO),ALO
                    AMEX Equity,"Almaden Minerals, Ltd. (AAU)",AAU
                    AMEX Equity,"Alpha Pro Tech, Ltd. (APT)",APT
                    AMEX Equity,Altisource Asset Management Corp (AAMC),AAMC
                    AMEX Equity,Ambow Education Holding Ltd. (AMBO),AMBO
                    AMEX Equity,AMCON Distributing Company (DIT),DIT
                    AMEX Equity,American Shared Hospital Services (AMS),AMS
                    AMEX Equity,Americas Silver Corporation (USAS),USAS
                    AMEX Equity,"Ampio Pharmaceuticals, Inc. (AMPE)",AMPE
                    AMEX Equity,Arconic Inc. (ARNC^),ARNC^
                    AMEX Equity,"Armata Pharmaceuticals, Inc. (ARMP)",ARMP
                    AMEX Equity,Asanko Gold Inc. (AKG),AKG
                    AMEX Equity,Ashford Inc. (AINC),AINC
                    AMEX Equity,Auryn Resources Inc. (AUG),AUG
                    AMEX Equity,Avalon Holdings Corporation (AWX),AWX
                    AMEX Equity,Avino Silver (ASM),ASM
                    AMEX Equity,B2Gold Corp (BTG),BTG
                    AMEX Equity,"Ballantyne Strong, Inc (BTN)",BTN
                    AMEX Equity,"Bancorp of New Jersey, Inc (BKJ)",BKJ
                    AMEX Equity,Bancroft Fund Limited (BCV),BCV
                    AMEX Equity,Bancroft Fund Limited (BCV^A),BCV^A
                    AMEX Equity,"Bar Harbor Bankshares, Inc. (BHB)",BHB
                    AMEX Equity,"Barnwell Industries, Inc. (BRN)",BRN
                    AMEX Equity,BG Staffing Inc (BGSF),BGSF
                    AMEX Equity,Bioceres Crop Solutions Corp. (BIOX),BIOX
                    AMEX Equity,Bioceres Crop Solutions Corp. (BIOX.WS),BIOX.WS
                    AMEX Equity,BioPharmX Corporation (BPMX),BPMX
                    AMEX Equity,"BioTime, Inc. (BTX)",BTX
                    AMEX Equity,Birks Group Inc. (BGI),BGI
                    AMEX Equity,BK Technologies Corporation (BKTI),BKTI
                    AMEX Equity,"Blonder Tongue Laboratories, Inc. (BDR)",BDR
                    AMEX Equity,"Bluerock Residential Growth REIT, Inc. (BRG)",BRG
                    AMEX Equity,"Bluerock Residential Growth REIT, Inc. (BRG^A)",BRG^A
                    AMEX Equity,"Bluerock Residential Growth REIT, Inc. (BRG^C)",BRG^C
                    AMEX Equity,"Bluerock Residential Growth REIT, Inc. (BRG^D)",BRG^D
                    AMEX Equity,BNY Mellon Municipal Income Inc. (DMF),DMF
                    AMEX Equity,"Bowl America, Inc. (BWL.A)",BWL.A
                    AMEX Equity,Caledonia Mining Corporation Plc (CMCL),CMCL
                    AMEX Equity,"Camber Energy, Inc. (CEI)",CEI
                    AMEX Equity,Can-Fite Biopharma Ltd (CANF),CANF
                    AMEX Equity,"Castle Brands, Inc. (ROX)",ROX
                    AMEX Equity,"cbdMD, Inc. (YCBD)",YCBD
                    AMEX Equity,Cel-Sci Corporation (CVM),CVM
                    AMEX Equity,Central Securities Corporation (CET),CET
                    AMEX Equity,Centrus Energy Corp. (LEU),LEU
                    AMEX Equity,Chardan Healthcare Acquisition Corp. (CHAC),CHAC
                    AMEX Equity,Chardan Healthcare Acquisition Corp. (CHAC.U),CHAC.U
                    AMEX Equity,Chardan Healthcare Acquisition Corp. (CHAC.WS),CHAC.WS
                    AMEX Equity,Chase Corporation (CCF),CCF
                    AMEX Equity,"Cheniere Energy Partners, LP (CQP)",CQP
                    AMEX Equity,"Cheniere Energy, Inc. (LNG)",LNG
                    AMEX Equity,Chicago Rivet & Machine Co. (CVR),CVR
                    AMEX Equity,"China Pharma Holdings, Inc. (CPHI)",CPHI
                    AMEX Equity,"CKX Lands, Inc. (CKX)",CKX
                    AMEX Equity,Clarivate Analytics Plc (CCC.WS),CCC.WS
                    AMEX Equity,Clough Global Dividend and Income Fund (GLV),GLV
                    AMEX Equity,Clough Global Equity Fund (GLQ),GLQ
                    AMEX Equity,Clough Global Opportunities Fund (GLO),GLO
                    AMEX Equity,Cohen & Company Inc. (COHN),COHN
                    AMEX Equity,CompX International Inc. (CIX),CIX
                    AMEX Equity,"Comstock Mining, Inc. (LODE)",LODE
                    AMEX Equity,"Condor Hospitality Trust, Inc. (CDOR)",CDOR
                    AMEX Equity,Consolidated-Tomoka Land Co. (CTO),CTO
                    AMEX Equity,Contango Oil & Gas Company (MCF),MCF
                    AMEX Equity,Continental Materials Corporation (CUO),CUO
                    AMEX Equity,Core Molding Technologies Inc (CMT),CMT
                    AMEX Equity,"Corindus Vascular Robotics, Inc. (CVRS)",CVRS
                    AMEX Equity,CorMedix Inc. (CRMD),CRMD
                    AMEX Equity,"Cornerstone Strategic Return Fund, Inc. (The) (CRF)",CRF
                    AMEX Equity,"Cornerstone Strategic Value Fund, Inc. (CLM)",CLM
                    AMEX Equity,"CPI Aerostructures, Inc. (CVU)",CVU
                    AMEX Equity,"Credit Suisse Asset Management Income Fund, Inc. (CIK)",CIK
                    AMEX Equity,Credit Suisse High Yield Bond Fund (DHY),DHY
                    AMEX Equity,CRH Medical Corporation (CRHM),CRHM
                    AMEX Equity,"CynergisTek, Inc. (CTEK)",CTEK
                    AMEX Equity,Daxor Corporation (DXR),DXR
                    AMEX Equity,"Delaware Investments Colorado Municipal Income Fund, Inc (VCF)",VCF
                    AMEX Equity,Delaware Investments Florida Insured Municipal Income Fund (VFL),VFL
                    AMEX Equity,"Delaware Investments Minnesota Municipal Income Fund II, Inc. (VMM)",VMM
                    AMEX Equity,"Delta Apparel, Inc. (DLA)",DLA
                    AMEX Equity,Denison Mine Corp (DNN),DNN
                    AMEX Equity,"DGSE Companies, Inc. (DGSE)",DGSE
                    AMEX Equity,"Document Security Systems, Inc. (DSS)",DSS
                    AMEX Equity,"DPW Holdings, Inc. (DPW)",DPW
                    AMEX Equity,Dunxin Financial Holdings Limited (DXF),DXF
                    AMEX Equity,"Eagle Capital Growth Fund, Inc. (GRF)",GRF
                    AMEX Equity,Eaton Vance California Municipal Bond Fund (EVM),EVM
                    AMEX Equity,Eaton Vance California Municipal Income Trust (CEV),CEV
                    AMEX Equity,Eaton Vance Limited Duration Income Fund (EVV),EVV
                    AMEX Equity,Eaton Vance Municipal Bond Fund (EIM),EIM
                    AMEX Equity,Eaton Vance New York Municipal Bond Fund (ENX),ENX
                    AMEX Equity,Eaton Vance New York Municipal Income Trust (EVY),EVY
                    AMEX Equity,"Electromed, Inc. (ELMD)",ELMD
                    AMEX Equity,Ellomay Capital Ltd. (ELLO),ELLO
                    AMEX Equity,Ellsworth Growth and Income Fund Ltd. (ECF),ECF
                    AMEX Equity,Ellsworth Growth and Income Fund Ltd. (ECF^A),ECF^A
                    AMEX Equity,eMagin Corporation (EMAN),EMAN
                    AMEX Equity,Emerson Radio Corporation (MSN),MSN
                    AMEX Equity,EMX Royalty Corporation (EMX),EMX
                    AMEX Equity,Energy Fuels Inc (UUUU),UUUU
                    AMEX Equity,Energy Fuels Inc (UUUU.WS),UUUU.WS
                    AMEX Equity,ENSERVCO Corporation (ENSV),ENSV
                    AMEX Equity,Entree Resources Ltd. (EGI),EGI
                    AMEX Equity,Espey Mfg. & Electronics Corp. (ESP),ESP
                    AMEX Equity,"Evans Bancorp, Inc. (EVBN)",EVBN
                    AMEX Equity,"EVI Industries, Inc. (EVI)",EVI
                    AMEX Equity,"Evolution Petroleum Corporation, Inc. (EPM)",EPM
                    AMEX Equity,First Trust Energy Income and Growth Fund (FEN),FEN
                    AMEX Equity,"Flanigan&#39;s Enterprises, Inc. (BDL)",BDL
                    AMEX Equity,Flexible Solutions International Inc. (FSI),FSI
                    AMEX Equity,Franklin Limited Duration Income Trust (FTF),FTF
                    AMEX Equity,Franklin Street Properties Corp. (FSP),FSP
                    AMEX Equity,Friedman Industries Inc. (FRD),FRD
                    AMEX Equity,"FTE Networks, Inc. (FTNW)",FTNW
                    AMEX Equity,"GAMCO Global Gold, Natural Reources & Income Trust  (GGN)",GGN
                    AMEX Equity,"GAMCO Global Gold, Natural Reources & Income Trust  (GGN^B)",GGN^B
                    AMEX Equity,GEE Group Inc. (JOB),JOB
                    AMEX Equity,"General Moly, Inc (GMO)",GMO
                    AMEX Equity,"GlobalSCAPE, Inc. (GSB)",GSB
                    AMEX Equity,"Globalstar, Inc. (GSAT)",GSAT
                    AMEX Equity,"Glowpoint, Inc. (GLOW)",GLOW
                    AMEX Equity,Gold Resource Corporation (GORO),GORO
                    AMEX Equity,Gold Standard Ventures Corporation (GSV),GSV
                    AMEX Equity,Golden Minerals Company (AUMN),AUMN
                    AMEX Equity,"Golden Star Resources, Ltd (GSS)",GSS
                    AMEX Equity,Goldfield Corporation (The) (GV),GV
                    AMEX Equity,Goodrich Petroleum Corporation (GDP),GDP
                    AMEX Equity,Gran Tierra Energy Inc. (GTE),GTE
                    AMEX Equity,Great Panther Mining Limited (GPL),GPL
                    AMEX Equity,"Grupo Simec, S.A. de C.V. (SIM)",SIM
                    AMEX Equity,"Hemispherx BioPharma, Inc. (HEB)",HEB
                    AMEX Equity,HEXO Corp. (HEXO),HEXO
                    AMEX Equity,Hillman Group Capital Trust (HLM^),HLM^
                    AMEX Equity,"HMG/Courtland Properties, Inc. (HMG)",HMG
                    AMEX Equity,Houston American Energy Corporation (HUSA),HUSA
                    AMEX Equity,"iBio, Inc. (IBIO)",IBIO
                    AMEX Equity,IBO (Listing Market - NYSE Amex Network B F) (IBO),IBO
                    AMEX Equity,IEC Electronics Corp. (IEC),IEC
                    AMEX Equity,"Impac Mortgage Holdings, Inc. (IMH)",IMH
                    AMEX Equity,Imperial Oil Limited (IMO),IMO
                    AMEX Equity,"Income Opportunity Realty Investors, Inc. (IOR)",IOR
                    AMEX Equity,India Globalization Capital Inc. (IGC),IGC
                    AMEX Equity,"InfuSystems Holdings, Inc. (INFU)",INFU
                    AMEX Equity,InnSuites Hospitality Trust (IHT),IHT
                    AMEX Equity,InspireMD Inc. (NSPR),NSPR
                    AMEX Equity,InspireMD Inc. (NSPR.WS),NSPR.WS
                    AMEX Equity,InspireMD Inc. (NSPR.WS.B),NSPR.WS.B
                    AMEX Equity,"Intellicheck, Inc. (IDN)",IDN
                    AMEX Equity,Intelligent Systems Corporation (INS),INS
                    AMEX Equity,International Tower Hill Mines Ltd (THM),THM
                    AMEX Equity,inTest Corporation (INTT),INTT
                    AMEX Equity,"Inuvo, Inc (INUV)",INUV
                    AMEX Equity,Invesco Advantage Municipal Income Trust II (VKI),VKI
                    AMEX Equity,"IsoRay, Inc. (ISR)",ISR
                    AMEX Equity,Issuer Direct Corporation (ISDR),ISDR
                    AMEX Equity,"IT Tech Packaging, Inc. (ITP)",ITP
                    AMEX Equity,Kelso Technologies Inc (KIQ),KIQ
                    AMEX Equity,Ladenburg Thalmann Financial Services Inc (LTS),LTS
                    AMEX Equity,Ladenburg Thalmann Financial Services Inc (LTS^A),LTS^A
                    AMEX Equity,Ladenburg Thalmann Financial Services Inc (LTSH),LTSH
                    AMEX Equity,Ladenburg Thalmann Financial Services Inc (LTSK),LTSK
                    AMEX Equity,Ladenburg Thalmann Financial Services Inc (LTSL),LTSL
                    AMEX Equity,Ladenburg Thalmann Financial Services Inc. (LTSF),LTSF
                    AMEX Equity,"LGL Group, Inc. (The) (LGL)",LGL
                    AMEX Equity,"Libbey, Inc. (LBY)",LBY
                    AMEX Equity,"Lilis Energy, Inc. (LLEX)",LLEX
                    AMEX Equity,MAG Silver Corporation (MAG),MAG
                    AMEX Equity,"Mastech Digital, Inc (MHH)",MHH
                    AMEX Equity,"Matinas Biopharma Holdings, Inc. (MTNB)",MTNB
                    AMEX Equity,Maverix Metals Inc. (MMX),MMX
                    AMEX Equity,McClatchy Company (The) (MNI),MNI
                    AMEX Equity,"Merrill Lynch & Co., Inc. 6.0518% Index Plus Trust Certificate (IPB)",IPB
                    AMEX Equity,Mexco Energy Corporation (MXC),MXC
                    AMEX Equity,MFS California Insured Municipal Trust (CCA),CCA
                    AMEX Equity,"Micron Solutions, Inc. (MICR)",MICR
                    AMEX Equity,"Milestone Scientific, Inc. (MLSS)",MLSS
                    AMEX Equity,Myomo Inc. (MYO),MYO
                    AMEX Equity,"NanoViricides, Inc. (NNVC)",NNVC
                    AMEX Equity,NASDAQ TEST STOCK (ATEST),ATEST
                    AMEX Equity,NASDAQ TEST STOCK (ATEST.A),ATEST.A
                    AMEX Equity,NASDAQ TEST STOCK (ATEST.B),ATEST.B
                    AMEX Equity,NASDAQ TEST STOCK (ATEST.C),ATEST.C
                    AMEX Equity,National HealthCare Corporation (NHC),NHC
                    AMEX Equity,"Navidea Biopharmaceuticals, Inc. (NAVB)",NAVB
                    AMEX Equity,"Network-1 Technologies, Inc. (NTIP)",NTIP
                    AMEX Equity,Neuberger Berman California Municipal Fund Inc (NBW),NBW
                    AMEX Equity,Neuberger Berman High Yield Strategies Fund (NHS),NHS
                    AMEX Equity,Neuberger Berman MLP and Energy Income Fund Inc. (NML),NML
                    AMEX Equity,Neuberger Berman Municipal Fund Inc. (NBH),NBH
                    AMEX Equity,Neuberger Berman New York Municipal Fund Inc. (NBO),NBO
                    AMEX Equity,"Neuberger Berman Real Estate Securities Income Fund, Inc. (NRO)",NRO
                    AMEX Equity,"New Concept Energy, Inc (GBR)",GBR
                    AMEX Equity,New England Realty Associates Limited Partnership (NEN),NEN
                    AMEX Equity,New Gold Inc. (NGD),NGD
                    AMEX Equity,Nexgen Energy Ltd. (NXE),NXE
                    AMEX Equity,Nobilis Health Corp. (HLTH),HLTH
                    AMEX Equity,"Northern Dynasty Minerals, Ltd. (NAK)",NAK
                    AMEX Equity,"Northern Oil and Gas, Inc. (NOG)",NOG
                    AMEX Equity,"NovaBay Pharmaceuticals, Inc. (NBY)",NBY
                    AMEX Equity,Novagold Resources Inc. (NG),NG
                    AMEX Equity,NRC Group Holdings Corp. (NRCG),NRCG
                    AMEX Equity,NRC Group Holdings Corp. (NRCG.WS),NRCG.WS
                    AMEX Equity,"NTN Buzztime, Inc. (NTN)",NTN
                    AMEX Equity,"Nuverra Environmental Solutions, Inc. (NES)",NES
                    AMEX Equity,OncoCyte Corporation (OCX),OCX
                    AMEX Equity,Oragenics Inc. (OGEN),OGEN
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^A),PCG^A
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^B),PCG^B
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^C),PCG^C
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^D),PCG^D
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^E),PCG^E
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^G),PCG^G
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^H),PCG^H
                    AMEX Equity,Pacific Gas & Electric Co. (PCG^I),PCG^I
                    AMEX Equity,"Palatin Technologies, Inc. (PTN)",PTN
                    AMEX Equity,Paramount Gold Nevada Corp. (PZG),PZG
                    AMEX Equity,Park National Corporation (PRK),PRK
                    AMEX Equity,Pedevco Corp. (PED),PED
                    AMEX Equity,Pfenex Inc. (PFNX),PFNX
                    AMEX Equity,Pioneer Diversified High Income Trust (HNW),HNW
                    AMEX Equity,Planet Green Holdings Corp (PLAG),PLAG
                    AMEX Equity,Platinum Group Metals Ltd. (PLG),PLG
                    AMEX Equity,"Plymouth Industrial REIT, Inc. (PLYM)",PLYM
                    AMEX Equity,"Plymouth Industrial REIT, Inc. (PLYM^A)",PLYM^A
                    AMEX Equity,Polymet Mining Corp. (PLM),PLM
                    AMEX Equity,Power REIT (PW),PW
                    AMEX Equity,Power REIT (PW^A),PW^A
                    AMEX Equity,"Protalix BioTherapeutics, Inc. (PLX)",PLX
                    AMEX Equity,"Radiant Logistics, Inc. (RLGT)",RLGT
                    AMEX Equity,"Rafael Holdings, Inc. (RFL)",RFL
                    AMEX Equity,Reaves Utility Income Fund (UTG),UTG
                    AMEX Equity,"Regional Health Properties, Inc. (RHE)",RHE
                    AMEX Equity,"Regional Health Properties, Inc. (RHE^A)",RHE^A
                    AMEX Equity,"RENN Fund, Inc. (RCG)",RCG
                    AMEX Equity,"Retractable Technologies, Inc. (RVP)",RVP
                    AMEX Equity,"Ring Energy, Inc. (REI)",REI
                    AMEX Equity,RMR Real Estate Income Fund (RIF),RIF
                    AMEX Equity,Sachem Capital Corp. (SACH),SACH
                    AMEX Equity,Sanchez Midstream Partners LP (SNMP),SNMP
                    AMEX Equity,Sandstorm Gold Ltd (SAND          ),SAND          
                    AMEX Equity,Seaboard Corporation (SEB),SEB
                    AMEX Equity,"Senseonics Holdings, Inc. (SENS)",SENS
                    AMEX Equity,"Servotronics, Inc. (SVT)",SVT
                    AMEX Equity,Sierra Metals Inc. (SMTS),SMTS
                    AMEX Equity,"SIFCO Industries, Inc. (SIF)",SIF
                    AMEX Equity,Silvercorp Metals Inc. (SVM),SVM
                    AMEX Equity,SilverCrest Metals Inc. (SILV),SILV
                    AMEX Equity,Solitario Zinc Corp. (XPL),XPL
                    AMEX Equity,Southern California Edison Company (SCE^B),SCE^B
                    AMEX Equity,Southern California Edison Company (SCE^C),SCE^C
                    AMEX Equity,Southern California Edison Company (SCE^D),SCE^D
                    AMEX Equity,Southern California Edison Company (SCE^E),SCE^E
                    AMEX Equity,Southwest Georgia Financial Corporation (SGB),SGB
                    AMEX Equity,"Spark Networks, Inc. (LOV)",LOV
                    AMEX Equity,SRC Energy Inc. (SRCI),SRCI
                    AMEX Equity,Standard Diversified Inc. (SDI),SDI
                    AMEX Equity,"SunLink Health Systems, Inc. (SSY)",SSY
                    AMEX Equity,"Superior Drilling Products, Inc. (SDPI)",SDPI
                    AMEX Equity,"Synthetic Biologics, Inc (SYN)",SYN
                    AMEX Equity,"Takung Art Co., Ltd. (TKAT)",TKAT
                    AMEX Equity,"Talos Energy, Inc. (TALO.WS)",TALO.WS
                    AMEX Equity,Tanzanian Gold Corporation (TRX),TRX
                    AMEX Equity,Taseko Mines Limited (TGB),TGB
                    AMEX Equity,"Tengasco, Inc. (TGC)",TGC
                    AMEX Equity,The Gabelli Global Utility and Income Trust (GLU),GLU
                    AMEX Equity,The Gabelli Global Utility and Income Trust (GLU^A),GLU^A
                    AMEX Equity,The Gabelli Global Utility and Income Trust (GLU^B),GLU^B
                    AMEX Equity,The Gabelli Go Anywhere Trust (GGO),GGO
                    AMEX Equity,The Gabelli Go Anywhere Trust (GGO^A),GGO^A
                    AMEX Equity,Tidewater Inc. (TDW.WS),TDW.WS
                    AMEX Equity,Tompkins Financial Corporation (TMP),TMP
                    AMEX Equity,Transatlantic Petroleum Ltd (TAT),TAT
                    AMEX Equity,"TransEnterix, Inc. (TRXC)",TRXC
                    AMEX Equity,Trilogy Metals Inc. (TMQ),TMQ
                    AMEX Equity,Trinity Place Holdings Inc. (TPHS),TPHS
                    AMEX Equity,Trio-Tech International (TRT),TRT
                    AMEX Equity,"Unique Fabricating, Inc. (UFAB)",UFAB
                    AMEX Equity,United States Antimony Corporation (UAMY),UAMY
                    AMEX Equity,"Universal Security Instruments, Inc. (UUU)",UUU
                    AMEX Equity,UQM Technologies Inc. (UQM),UQM
                    AMEX Equity,Ur Energy Inc (URG),URG
                    AMEX Equity,Uranium Energy Corp. (UEC),UEC
                    AMEX Equity,VirnetX Holding Corp (VHC),VHC
                    AMEX Equity,Vista Gold Corporation (VGZ),VGZ
                    AMEX Equity,VolitionRX Limited (VNRX),VNRX
                    AMEX Equity,"Volt Information Sciences, Inc. (VISI)",VISI
                    AMEX Equity,Wells Fargo Income Opportunities Fund (EAD),EAD
                    AMEX Equity,Wells Fargo Multi-Sector Income Fund (ERC),ERC
                    AMEX Equity,Wells Fargo Utilities and High Income Fund (ERH),ERH
                    AMEX Equity,Western Copper and Gold Corporation (WRN),WRN
                    AMEX Equity,WidePoint Corporation (WYY),WYY
                    AMEX Equity,"Wireless Telecom Group,  Inc. (WTT)",WTT
                    AMEX Equity,"Xtant Medical Holdings, Inc. (XTNT)",XTNT
                    AMEX Equity,"Yuma Energy, Inc. (YUMA)",YUMA
                    AMEX Equity,"Zedge, Inc. (ZDGE)",ZDGE
                    AMEX Equity,Zomedica Pharmaceuticals Corp. (ZOM),ZOM
                    NASDAQ Equity,"111, Inc. (YI)",YI
                    NASDAQ Equity,"1347 Property Insurance Holdings, Inc. (PIH)",PIH
                    NASDAQ Equity,"1347 Property Insurance Holdings, Inc. (PIHPP)",PIHPP
                    NASDAQ Equity,180 Degree Capital Corp. (TURN),TURN
                    NASDAQ Equity,"1-800 FLOWERS.COM, Inc. (FLWS)",FLWS
                    NASDAQ Equity,"1895 Bancorp of Wisconsin, Inc. (BCOW)",BCOW
                    NASDAQ Equity,1st Constitution Bancorp (NJ) (FCCY),FCCY
                    NASDAQ Equity,1st Source Corporation (SRCE),SRCE
                    NASDAQ Equity,"21Vianet Group, Inc. (VNET)",VNET
                    NASDAQ Equity,"2U, Inc. (TWOU)",TWOU
                    NASDAQ Equity,"360 Finance, Inc. (QFIN)",QFIN
                    NASDAQ Equity,"51job, Inc. (JOBS)",JOBS
                    NASDAQ Equity,8i Enterprises Acquisition Corp (JFK),JFK
                    NASDAQ Equity,8i Enterprises Acquisition Corp (JFKKR),JFKKR
                    NASDAQ Equity,8i Enterprises Acquisition Corp (JFKKU),JFKKU
                    NASDAQ Equity,8i Enterprises Acquisition Corp (JFKKW),JFKKW
                    NASDAQ Equity,8x8 Inc (EGHT),EGHT
                    NASDAQ Equity,"AAON, Inc. (AAON)",AAON
                    NASDAQ Equity,Abeona Therapeutics Inc. (ABEO),ABEO
                    NASDAQ Equity,Abeona Therapeutics Inc. (ABEOW),ABEOW
                    NASDAQ Equity,Ability Inc. (ABIL),ABIL
                    NASDAQ Equity,"ABIOMED, Inc. (ABMD)",ABMD
                    NASDAQ Equity,Abraxas Petroleum Corporation (AXAS),AXAS
                    NASDAQ Equity,AC Immune SA (ACIU),ACIU
                    NASDAQ Equity,"Acacia Communications, Inc. (ACIA)",ACIA
                    NASDAQ Equity,Acacia Research Corporation (ACTG),ACTG
                    NASDAQ Equity,"Acadia Healthcare Company, Inc. (ACHC)",ACHC
                    NASDAQ Equity,ACADIA Pharmaceuticals Inc. (ACAD),ACAD
                    NASDAQ Equity,Acamar Partners Acquisition Corp. (ACAM),ACAM
                    NASDAQ Equity,Acamar Partners Acquisition Corp. (ACAMU),ACAMU
                    NASDAQ Equity,Acamar Partners Acquisition Corp. (ACAMW),ACAMW
                    NASDAQ Equity,"Acasti Pharma, Inc. (ACST)",ACST
                    NASDAQ Equity,"Accelerate Diagnostics, Inc. (AXDX)",AXDX
                    NASDAQ Equity,Acceleron Pharma Inc. (XLRN),XLRN
                    NASDAQ Equity,Accuray Incorporated (ARAY),ARAY
                    NASDAQ Equity,"AcelRx Pharmaceuticals, Inc. (ACRX)",ACRX
                    NASDAQ Equity,Acer Therapeutics Inc. (ACER),ACER
                    NASDAQ Equity,"Achieve Life Sciences, Inc.  (ACHV)",ACHV
                    NASDAQ Equity,"Achillion Pharmaceuticals, Inc. (ACHN)",ACHN
                    NASDAQ Equity,"ACI Worldwide, Inc. (ACIW)",ACIW
                    NASDAQ Equity,"Aclaris Therapeutics, Inc. (ACRS)",ACRS
                    NASDAQ Equity,"ACM Research, Inc. (ACMR)",ACMR
                    NASDAQ Equity,ACNB Corporation (ACNB),ACNB
                    NASDAQ Equity,"Acorda Therapeutics, Inc. (ACOR)",ACOR
                    NASDAQ Equity,Act II Global Acquisition Corp. (ACTT),ACTT
                    NASDAQ Equity,Act II Global Acquisition Corp. (ACTTU),ACTTU
                    NASDAQ Equity,Act II Global Acquisition Corp. (ACTTW),ACTTW
                    NASDAQ Equity,"Activision Blizzard, Inc (ATVI)",ATVI
                    NASDAQ Equity,"Adamas Pharmaceuticals, Inc. (ADMS)",ADMS
                    NASDAQ Equity,Adamis Pharmaceuticals Corporation (ADMP),ADMP
                    NASDAQ Equity,Adaptimmune Therapeutics plc (ADAP),ADAP
                    NASDAQ Equity,Addus HomeCare Corporation (ADUS),ADUS
                    NASDAQ Equity,"ADDvantage Technologies Group, Inc. (AEY)",AEY
                    NASDAQ Equity,Adesto Technologies Corporation (IOTS),IOTS
                    NASDAQ Equity,"Adial Pharmaceuticals, Inc (ADIL)",ADIL
                    NASDAQ Equity,"Adial Pharmaceuticals, Inc (ADILW)",ADILW
                    NASDAQ Equity,ADMA Biologics Inc (ADMA),ADMA
                    NASDAQ Equity,Adobe Inc. (ADBE),ADBE
                    NASDAQ Equity,"ADOMANI, Inc. (ADOM)",ADOM
                    NASDAQ Equity,"ADTRAN, Inc. (ADTN)",ADTN
                    NASDAQ Equity,"Aduro Biotech, Inc. (ADRO)",ADRO
                    NASDAQ Equity,"Advanced Emissions Solutions, Inc. (ADES)",ADES
                    NASDAQ Equity,"Advanced Energy Industries, Inc. (AEIS)",AEIS
                    NASDAQ Equity,"Advanced Micro Devices, Inc. (AMD)",AMD
                    NASDAQ Equity,"Advaxis, Inc. (ADXS)",ADXS
                    NASDAQ Equity,"Adverum Biotechnologies, Inc. (ADVM)",ADVM
                    NASDAQ Equity,AdvisorShares Dorsey Wright Micro-Cap ETF (DWMC),DWMC
                    NASDAQ Equity,AdvisorShares Dorsey Wright Short ETF (DWSH),DWSH
                    NASDAQ Equity,AdvisorShares Sabretooth ETF (BKCH),BKCH
                    NASDAQ Equity,AdvisorShares Vice ETF (ACT),ACT
                    NASDAQ Equity,Aegion Corp (AEGN),AEGN
                    NASDAQ Equity,"Aeglea BioTherapeutics, Inc. (AGLE)",AGLE
                    NASDAQ Equity,Aehr Test Systems (AEHR),AEHR
                    NASDAQ Equity,"Aemetis, Inc (AMTX)",AMTX
                    NASDAQ Equity,"Aerie Pharmaceuticals, Inc. (AERI)",AERI
                    NASDAQ Equity,"AeroVironment, Inc. (AVAV)",AVAV
                    NASDAQ Equity,"Aerpio Pharmaceuticals, Inc. (ARPO)",ARPO
                    NASDAQ Equity,AEterna Zentaris Inc. (AEZS),AEZS
                    NASDAQ Equity,"Aethlon Medical, Inc. (AEMD)",AEMD
                    NASDAQ Equity,"Aevi Genomic Medicine, Inc. (GNMX)",GNMX
                    NASDAQ Equity,Affimed N.V. (AFMD),AFMD
                    NASDAQ Equity,AGBA Acquisition Limited (AGBAU),AGBAU
                    NASDAQ Equity,Agenus Inc. (AGEN),AGEN
                    NASDAQ Equity,"Agile Therapeutics, Inc. (AGRX)",AGRX
                    NASDAQ Equity,"Agilysys, Inc. (AGYS)",AGYS
                    NASDAQ Equity,"Agios Pharmaceuticals, Inc. (AGIO)",AGIO
                    NASDAQ Equity,AGM Group Holdings Inc. (AGMH),AGMH
                    NASDAQ Equity,AGNC Investment Corp. (AGNC),AGNC
                    NASDAQ Equity,AGNC Investment Corp. (AGNCB),AGNCB
                    NASDAQ Equity,AGNC Investment Corp. (AGNCM),AGNCM
                    NASDAQ Equity,AGNC Investment Corp. (AGNCN),AGNCN
                    NASDAQ Equity,"AgroFresh Solutions, Inc. (AGFS)",AGFS
                    NASDAQ Equity,"AgroFresh Solutions, Inc. (AGFSW)",AGFSW
                    NASDAQ Equity,"Aileron Therapeutics, Inc. (ALRN)",ALRN
                    NASDAQ Equity,"Aimmune Therapeutics, Inc. (AIMT)",AIMT
                    NASDAQ Equity,"Air T, Inc. (AIRT)",AIRT
                    NASDAQ Equity,"Air T, Inc. (AIRTP)",AIRTP
                    NASDAQ Equity,"Air T, Inc. (AIRTW)",AIRTW
                    NASDAQ Equity,"Air Transport Services Group, Inc (ATSG)",ATSG
                    NASDAQ Equity,"Airgain, Inc. (AIRG)",AIRG
                    NASDAQ Equity,AirNet Technology Inc. (ANTE),ANTE
                    NASDAQ Equity,"AIT Therapeutics, Inc. (AITB)",AITB
                    NASDAQ Equity,"Akamai Technologies, Inc. (AKAM)",AKAM
                    NASDAQ Equity,Akari Therapeutics Plc (AKTX),AKTX
                    NASDAQ Equity,"Akcea Therapeutics, Inc. (AKCA)",AKCA
                    NASDAQ Equity,"Akebia Therapeutics, Inc. (AKBA)",AKBA
                    NASDAQ Equity,Akerna Corp. (KERN),KERN
                    NASDAQ Equity,Akerna Corp. (KERNW),KERNW
                    NASDAQ Equity,"Akero Therapeutics, Inc. (AKRO)",AKRO
                    NASDAQ Equity,Akers Biosciences Inc. (AKER),AKER
                    NASDAQ Equity,"Akorn, Inc. (AKRX)",AKRX
                    NASDAQ Equity,"Akoustis Technologies, Inc. (AKTS)",AKTS
                    NASDAQ Equity,"Alarm.com Holdings, Inc. (ALRM)",ALRM
                    NASDAQ Equity,"Alaska Communications Systems Group, Inc. (ALSK)",ALSK
                    NASDAQ Equity,Alberton Acquisition Corporation (ALAC),ALAC
                    NASDAQ Equity,Alberton Acquisition Corporation (ALACR),ALACR
                    NASDAQ Equity,Alberton Acquisition Corporation (ALACU),ALACU
                    NASDAQ Equity,Alberton Acquisition Corporation (ALACW),ALACW
                    NASDAQ Equity,"Albireo Pharma, Inc. (ALBO)",ALBO
                    NASDAQ Equity,Alcentra Capital Corp. (ABDC),ABDC
                    NASDAQ Equity,"Alder BioPharmaceuticals, Inc. (ALDR)",ALDR
                    NASDAQ Equity,"Aldeyra Therapeutics, Inc. (ALDX)",ALDX
                    NASDAQ Equity,"Alector, Inc. (ALEC)",ALEC
                    NASDAQ Equity,"Alexion Pharmaceuticals, Inc. (ALXN)",ALXN
                    NASDAQ Equity,"Alico, Inc. (ALCO)",ALCO
                    NASDAQ Equity,"Align Technology, Inc. (ALGN)",ALGN
                    NASDAQ Equity,"Alimera Sciences, Inc. (ALIM)",ALIM
                    NASDAQ Equity,Alithya Group inc. (ALYA),ALYA
                    NASDAQ Equity,"ALJ Regional Holdings, Inc. (ALJJ)",ALJJ
                    NASDAQ Equity,Alkermes plc (ALKS),ALKS
                    NASDAQ Equity,Allakos Inc. (ALLK),ALLK
                    NASDAQ Equity,"Allegiance Bancshares, Inc. (ABTX)",ABTX
                    NASDAQ Equity,Allegiant Travel Company (ALGT),ALGT
                    NASDAQ Equity,Allegro Merger Corp. (ALGR),ALGR
                    NASDAQ Equity,Allegro Merger Corp. (ALGRR),ALGRR
                    NASDAQ Equity,Allegro Merger Corp. (ALGRU),ALGRU
                    NASDAQ Equity,Allegro Merger Corp. (ALGRW),ALGRW
                    NASDAQ Equity,"Allena Pharmaceuticals, Inc. (ALNA)",ALNA
                    NASDAQ Equity,"Alliance Resource Partners, L.P. (ARLP)",ARLP
                    NASDAQ Equity,Alliant Energy Corporation (LNT),LNT
                    NASDAQ Equity,"Allied Healthcare Products, Inc. (AHPI)",AHPI
                    NASDAQ Equity,"Allied Motion Technologies, Inc. (AMOT)",AMOT
                    NASDAQ Equity,"Allogene Therapeutics, Inc. (ALLO)",ALLO
                    NASDAQ Equity,Allot Ltd. (ALLT),ALLT
                    NASDAQ Equity,"Allscripts Healthcare Solutions, Inc. (MDRX)",MDRX
                    NASDAQ Equity,"Alnylam Pharmaceuticals, Inc. (ALNY)",ALNY
                    NASDAQ Equity,Alpha and Omega Semiconductor Limited (AOSL),AOSL
                    NASDAQ Equity,Alphabet Inc. (GOOG),GOOG
                    NASDAQ Equity,Alphabet Inc. (GOOGL),GOOGL
                    NASDAQ Equity,AlphaMark Actively Managed Small Cap ETF (SMCP),SMCP
                    NASDAQ Equity,"Alphatec Holdings, Inc. (ATEC)",ATEC
                    NASDAQ Equity,"Alpine Immune Sciences, Inc. (ALPN)",ALPN
                    NASDAQ Equity,"Alta Mesa Resources, Inc. (AMR)",AMR
                    NASDAQ Equity,"Alta Mesa Resources, Inc. (AMRWW)",AMRWW
                    NASDAQ Equity,Altaba Inc. (AABA),AABA
                    NASDAQ Equity,Altair Engineering Inc. (ALTR),ALTR
                    NASDAQ Equity,Alterity Therapeutics Limited (ATHE),ATHE
                    NASDAQ Equity,"Altimmune, Inc. (ALT)",ALT
                    NASDAQ Equity,Altisource Portfolio Solutions S.A. (ASPS),ASPS
                    NASDAQ Equity,Altra Industrial Motion Corp. (AIMC),AIMC
                    NASDAQ Equity,Altus Midstream Company (ALTM),ALTM
                    NASDAQ Equity,"AMAG Pharmaceuticals, Inc. (AMAG)",AMAG
                    NASDAQ Equity,Amalgamated Bank (AMAL),AMAL
                    NASDAQ Equity,Amarin Corporation plc (AMRN),AMRN
                    NASDAQ Equity,"A-Mark Precious Metals, Inc. (AMRK)",AMRK
                    NASDAQ Equity,"Amazon.com, Inc. (AMZN)",AMZN
                    NASDAQ Equity,"Ambac Financial Group, Inc. (AMBC)",AMBC
                    NASDAQ Equity,"Ambac Financial Group, Inc. (AMBCW)",AMBCW
                    NASDAQ Equity,"Ambarella, Inc. (AMBA)",AMBA
                    NASDAQ Equity,AMC Networks Inc. (AMCX),AMCX
                    NASDAQ Equity,AMCI Acquisition Corp. (AMCI),AMCI
                    NASDAQ Equity,AMCI Acquisition Corp. (AMCIU),AMCIU
                    NASDAQ Equity,AMCI Acquisition Corp. (AMCIW),AMCIW
                    NASDAQ Equity,Amdocs Limited (DOX),DOX
                    NASDAQ Equity,Amedisys Inc (AMED),AMED
                    NASDAQ Equity,Amerant Bancorp Inc. (AMTB),AMTB
                    NASDAQ Equity,Amerant Bancorp Inc. (AMTBB),AMTBB
                    NASDAQ Equity,Amerco (UHAL),UHAL
                    NASDAQ Equity,"Ameri Holdings, Inc. (AMRH)",AMRH
                    NASDAQ Equity,"Ameri Holdings, Inc. (AMRHW)",AMRHW
                    NASDAQ Equity,"America First Multifamily Investors, L.P. (ATAX)",ATAX
                    NASDAQ Equity,"America Movil, S.A.B. de C.V. (AMOV)",AMOV
                    NASDAQ Equity,"American Airlines Group, Inc. (AAL)",AAL
                    NASDAQ Equity,"American Electric Technologies, Inc. (AETI)",AETI
                    NASDAQ Equity,"American Finance Trust, Inc. (AFIN)",AFIN
                    NASDAQ Equity,"American Finance Trust, Inc. (AFINP)",AFINP
                    NASDAQ Equity,"American National Bankshares, Inc. (AMNB)",AMNB
                    NASDAQ Equity,American National Insurance Company (ANAT),ANAT
                    NASDAQ Equity,American Outdoor Brands Corporation (AOBC),AOBC
                    NASDAQ Equity,"American Public Education, Inc. (APEI)",APEI
                    NASDAQ Equity,American Resources Corporation (AREC),AREC
                    NASDAQ Equity,American River Bankshares (AMRB),AMRB
                    NASDAQ Equity,"American Software, Inc. (AMSWA)",AMSWA
                    NASDAQ Equity,American Superconductor Corporation (AMSC),AMSC
                    NASDAQ Equity,American Woodmark Corporation (AMWD),AMWD
                    NASDAQ Equity,"America&#39;s Car-Mart, Inc. (CRMT)",CRMT
                    NASDAQ Equity,Ameris Bancorp (ABCB),ABCB
                    NASDAQ Equity,"AMERISAFE, Inc. (AMSF)",AMSF
                    NASDAQ Equity,AmeriServ Financial Inc. (ASRV),ASRV
                    NASDAQ Equity,AmeriServ Financial Inc. (ASRVP),ASRVP
                    NASDAQ Equity,Ames National Corporation (ATLO),ATLO
                    NASDAQ Equity,Amgen Inc. (AMGN),AMGN
                    NASDAQ Equity,"Amicus Therapeutics, Inc. (FOLD)",FOLD
                    NASDAQ Equity,"Amkor Technology, Inc. (AMKR)",AMKR
                    NASDAQ Equity,"Amphastar Pharmaceuticals, Inc. (AMPH)",AMPH
                    NASDAQ Equity,Amplify Online Retail ETF (IBUY),IBUY
                    NASDAQ Equity,"Amtech Systems, Inc. (ASYS)",ASYS
                    NASDAQ Equity,"Amyris, Inc. (AMRS)",AMRS
                    NASDAQ Equity,"Analog Devices, Inc. (ADI)",ADI
                    NASDAQ Equity,"AnaptysBio, Inc. (ANAB)",ANAB
                    NASDAQ Equity,Anavex Life Sciences Corp. (AVXL),AVXL
                    NASDAQ Equity,Anchiano Therapeutics Ltd. (ANCN),ANCN
                    NASDAQ Equity,Andina Acquisition Corp. III (ANDA),ANDA
                    NASDAQ Equity,Andina Acquisition Corp. III (ANDAR),ANDAR
                    NASDAQ Equity,Andina Acquisition Corp. III (ANDAU),ANDAU
                    NASDAQ Equity,Andina Acquisition Corp. III (ANDAW),ANDAW
                    NASDAQ Equity,ANGI Homeservices Inc. (ANGI),ANGI
                    NASDAQ Equity,"AngioDynamics, Inc. (ANGO)",ANGO
                    NASDAQ Equity,"ANI Pharmaceuticals, Inc. (ANIP)",ANIP
                    NASDAQ Equity,Anika Therapeutics Inc. (ANIK),ANIK
                    NASDAQ Equity,"Anixa Biosciences, Inc. (ANIX)",ANIX
                    NASDAQ Equity,"ANSYS, Inc. (ANSS)",ANSS
                    NASDAQ Equity,"Antares Pharma, Inc. (ATRS)",ATRS
                    NASDAQ Equity,"Apellis Pharmaceuticals, Inc. (APLS)",APLS
                    NASDAQ Equity,"Apogee Enterprises, Inc. (APOG)",APOG
                    NASDAQ Equity,"Apollo Endosurgery, Inc. (APEN)",APEN
                    NASDAQ Equity,Apollo Investment Corporation (AINV),AINV
                    NASDAQ Equity,"Apollo Medical Holdings, Inc. (AMEH)",AMEH
                    NASDAQ Equity,"AppFolio, Inc. (APPF)",APPF
                    NASDAQ Equity,Appian Corporation (APPN),APPN
                    NASDAQ Equity,Apple Inc. (AAPL),AAPL
                    NASDAQ Equity,"Appliance Recycling Centers of America, Inc. (ARCI)",ARCI
                    NASDAQ Equity,Applied DNA Sciences Inc (APDN),APDN
                    NASDAQ Equity,Applied DNA Sciences Inc (APDNW),APDNW
                    NASDAQ Equity,Applied Genetic Technologies Corporation (AGTC),AGTC
                    NASDAQ Equity,"Applied Materials, Inc. (AMAT)",AMAT
                    NASDAQ Equity,"Applied Optoelectronics, Inc. (AAOI)",AAOI
                    NASDAQ Equity,"Applied Therapeutics, Inc. (APLT)",APLT
                    NASDAQ Equity,Approach Resources Inc. (AREX),AREX
                    NASDAQ Equity,Aptevo Therapeutics Inc. (APVO),APVO
                    NASDAQ Equity,Aptinyx Inc. (APTX),APTX
                    NASDAQ Equity,Aptorum Group Limited (APM),APM
                    NASDAQ Equity,"Aptose Biosciences, Inc. (APTO)",APTO
                    NASDAQ Equity,Apyx Medical Corporation (APYX),APYX
                    NASDAQ Equity,"Aqua Metals, Inc. (AQMS)",AQMS
                    NASDAQ Equity,"AquaBounty Technologies, Inc. (AQB)",AQB
                    NASDAQ Equity,"Aquestive Therapeutics, Inc. (AQST)",AQST
                    NASDAQ Equity,"Aquinox Pharmaceuticals, Inc. (AQXP)",AQXP
                    NASDAQ Equity,"Aratana Therapeutics, Inc. (PETX)",PETX
                    NASDAQ Equity,"Aravive, Inc. (ARAV)",ARAV
                    NASDAQ Equity,Arbutus Biopharma Corporation (ABUS),ABUS
                    NASDAQ Equity,"ARC Group Worldwide, Inc. (ARCW)",ARCW
                    NASDAQ Equity,"ARCA biopharma, Inc. (ABIO)",ABIO
                    NASDAQ Equity,"Arcadia Biosciences, Inc. (RKDA)",RKDA
                    NASDAQ Equity,ArcBest Corporation (ARCB),ARCB
                    NASDAQ Equity,Arch Capital Group Ltd. (ACGL),ACGL
                    NASDAQ Equity,Arch Capital Group Ltd. (ACGLO),ACGLO
                    NASDAQ Equity,Arch Capital Group Ltd. (ACGLP),ACGLP
                    NASDAQ Equity,"Arcimoto, Inc. (FUV)",FUV
                    NASDAQ Equity,Arco Platform Limited (ARCE),ARCE
                    NASDAQ Equity,Arcturus Therapeutics Holdings Inc. (ARCT),ARCT
                    NASDAQ Equity,"Ardelyx, Inc. (ARDX)",ARDX
                    NASDAQ Equity,"Arena Pharmaceuticals, Inc. (ARNA)",ARNA
                    NASDAQ Equity,Ares Capital Corporation (ARCC),ARCC
                    NASDAQ Equity,argenx SE (ARGX),ARGX
                    NASDAQ Equity,Aridis Pharmaceuticals Inc. (ARDS),ARDS
                    NASDAQ Equity,Ark Restaurants Corp. (ARKR),ARKR
                    NASDAQ Equity,Arotech Corporation (ARTX),ARTX
                    NASDAQ Equity,"ArQule, Inc. (ARQL)",ARQL
                    NASDAQ Equity,Array BioPharma Inc. (ARRY),ARRY
                    NASDAQ Equity,Arrow DWA Country Rotation ETF (DWCR),DWCR
                    NASDAQ Equity,Arrow DWA Tactical ETF (DWAT),DWAT
                    NASDAQ Equity,Arrow Financial Corporation (AROW),AROW
                    NASDAQ Equity,"Arrowhead Pharmaceuticals, Inc. (ARWR)",ARWR
                    NASDAQ Equity,"Artelo Biosciences, Inc. (ARTL)",ARTL
                    NASDAQ Equity,"Artelo Biosciences, Inc. (ARTLW)",ARTLW
                    NASDAQ Equity,Artesian Resources Corporation (ARTNA),ARTNA
                    NASDAQ Equity,"Art&#39;s-Way Manufacturing Co., Inc. (ARTW)",ARTW
                    NASDAQ Equity,"Arvinas, Inc. (ARVN)",ARVN
                    NASDAQ Equity,ARYA Sciences Acquisition Corp. (ARYA),ARYA
                    NASDAQ Equity,ARYA Sciences Acquisition Corp. (ARYAU),ARYAU
                    NASDAQ Equity,ARYA Sciences Acquisition Corp. (ARYAW),ARYAW
                    NASDAQ Equity,"Ascena Retail Group, Inc. (ASNA)",ASNA
                    NASDAQ Equity,Ascendis Pharma A/S (ASND),ASND
                    NASDAQ Equity,"Ascent Capital Group, Inc. (ASCMA)",ASCMA
                    NASDAQ Equity,Asia Pacific Wire & Cable Corporation Limited (APWC),APWC
                    NASDAQ Equity,ASLAN Pharmaceuticals Limited (ASLN),ASLN
                    NASDAQ Equity,ASML Holding N.V. (ASML),ASML
                    NASDAQ Equity,Aspen Group Inc. (ASPU),ASPU
                    NASDAQ Equity,"Aspen Technology, Inc. (AZPN)",AZPN
                    NASDAQ Equity,"Assembly Biosciences, Inc. (ASMB)",ASMB
                    NASDAQ Equity,"Assertio Therapeutics, Inc. (ASRT)",ASRT
                    NASDAQ Equity,"Asta Funding, Inc. (ASFI)",ASFI
                    NASDAQ Equity,"Astec Industries, Inc. (ASTE)",ASTE
                    NASDAQ Equity,Astronics Corporation (ATRO),ATRO
                    NASDAQ Equity,"AstroNova, Inc. (ALOT)",ALOT
                    NASDAQ Equity,Astrotech Corporation (ASTC),ASTC
                    NASDAQ Equity,Asure Software Inc (ASUR),ASUR
                    NASDAQ Equity,"ASV Holdings, Inc. (ASV)",ASV
                    NASDAQ Equity,ATA Inc. (ATAI),ATAI
                    NASDAQ Equity,"Atara Biotherapeutics, Inc. (ATRA)",ATRA
                    NASDAQ Equity,"Athenex, Inc. (ATNX)",ATNX
                    NASDAQ Equity,"Athersys, Inc. (ATHX)",ATHX
                    NASDAQ Equity,ATIF Holdings Limited (ATIF),ATIF
                    NASDAQ Equity,Atlantic American Corporation (AAME),AAME
                    NASDAQ Equity,"Atlantic Capital Bancshares, Inc. (ACBI)",ACBI
                    NASDAQ Equity,Atlantic Union Bankshares Corporation (AUB),AUB
                    NASDAQ Equity,Atlantica Yield plc (AY),AY
                    NASDAQ Equity,Atlanticus Holdings Corporation (ATLC),ATLC
                    NASDAQ Equity,Atlas Air Worldwide Holdings (AAWW),AAWW
                    NASDAQ Equity,"Atlas Financial Holdings, Inc. (AFH)",AFH
                    NASDAQ Equity,"Atlas Financial Holdings, Inc. (AFHBL)",AFHBL
                    NASDAQ Equity,Atlassian Corporation Plc (TEAM),TEAM
                    NASDAQ Equity,"ATN International, Inc. (ATNI)",ATNI
                    NASDAQ Equity,Atomera Incorporated (ATOM),ATOM
                    NASDAQ Equity,Atossa Genetics Inc. (ATOS),ATOS
                    NASDAQ Equity,"Atreca, Inc. (BCEL)",BCEL
                    NASDAQ Equity,"AtriCure, Inc. (ATRC)",ATRC
                    NASDAQ Equity,Atrion Corporation (ATRI),ATRI
                    NASDAQ Equity,Attis Industries Inc. (ATIS),ATIS
                    NASDAQ Equity,Attis Industries Inc. (ATISW),ATISW
                    NASDAQ Equity,"aTyr Pharma, Inc. (LIFE)",LIFE
                    NASDAQ Equity,"Auburn National Bancorporation, Inc. (AUBN)",AUBN
                    NASDAQ Equity,"Audentes Therapeutics, Inc. (BOLD)",BOLD
                    NASDAQ Equity,AudioCodes Ltd. (AUDC),AUDC
                    NASDAQ Equity,"AudioEye, Inc. (AEYE)",AEYE
                    NASDAQ Equity,Aurinia Pharmaceuticals Inc (AUPH),AUPH
                    NASDAQ Equity,Auris Medical Holding Ltd. (EARS),EARS
                    NASDAQ Equity,Aurora Mobile Limited (JG),JG
                    NASDAQ Equity,"Autodesk, Inc. (ADSK)",ADSK
                    NASDAQ Equity,Autolus Therapeutics plc (AUTL),AUTL
                    NASDAQ Equity,"Automatic Data Processing, Inc. (ADP)",ADP
                    NASDAQ Equity,"AutoWeb, Inc. (AUTO)",AUTO
                    NASDAQ Equity,Avadel Pharmaceuticals plc (AVDL),AVDL
                    NASDAQ Equity,Avalon GloboCare Corp. (AVCO),AVCO
                    NASDAQ Equity,"Avedro, Inc (AVDR)",AVDR
                    NASDAQ Equity,"Avenue Therapeutics, Inc. (ATXI)",ATXI
                    NASDAQ Equity,"AVEO Pharmaceuticals, Inc. (AVEO)",AVEO
                    NASDAQ Equity,"Aviat Networks, Inc. (AVNW)",AVNW
                    NASDAQ Equity,"Avid Bioservices, Inc. (CDMO)",CDMO
                    NASDAQ Equity,"Avid Bioservices, Inc. (CDMOP)",CDMOP
                    NASDAQ Equity,"Avid Technology, Inc. (AVID)",AVID
                    NASDAQ Equity,"Avinger, Inc. (AVGR)",AVGR
                    NASDAQ Equity,"Avis Budget Group, Inc. (CAR)",CAR
                    NASDAQ Equity,"Avnet, Inc. (AVT)",AVT
                    NASDAQ Equity,"AVROBIO, Inc. (AVRO)",AVRO
                    NASDAQ Equity,"Aware, Inc. (AWRE)",AWRE
                    NASDAQ Equity,"Axcelis Technologies, Inc. (ACLS)",ACLS
                    NASDAQ Equity,Axcella Health Inc. (AXLA),AXLA
                    NASDAQ Equity,"AxoGen, Inc. (AXGN)",AXGN
                    NASDAQ Equity,"Axon Enterprise, Inc. (AAXN)",AAXN
                    NASDAQ Equity,"Axonics Modulation Technologies, Inc. (AXNX)",AXNX
                    NASDAQ Equity,Axovant Gene Therapies Ltd. (AXGT),AXGT
                    NASDAQ Equity,"Axsome Therapeutics, Inc. (AXSM)",AXSM
                    NASDAQ Equity,AXT Inc (AXTI),AXTI
                    NASDAQ Equity,"Aytu BioScience, Inc. (AYTU)",AYTU
                    NASDAQ Equity,"AzurRx BioPharma, Inc. (AZRX)",AZRX
                    NASDAQ Equity,B Communications Ltd. (BCOM),BCOM
                    NASDAQ Equity,"B. Riley Financial, Inc. (RILY)",RILY
                    NASDAQ Equity,"B. Riley Financial, Inc. (RILYG)",RILYG
                    NASDAQ Equity,"B. Riley Financial, Inc. (RILYH)",RILYH
                    NASDAQ Equity,"B. Riley Financial, Inc. (RILYI)",RILYI
                    NASDAQ Equity,"B. Riley Financial, Inc. (RILYL)",RILYL
                    NASDAQ Equity,"B. Riley Financial, Inc. (RILYO)",RILYO
                    NASDAQ Equity,"B. Riley Financial, Inc. (RILYZ)",RILYZ
                    NASDAQ Equity,B.O.S. Better Online Solutions (BOSC),BOSC
                    NASDAQ Equity,"Baidu, Inc. (BIDU)",BIDU
                    NASDAQ Equity,Balchem Corporation (BCPC),BCPC
                    NASDAQ Equity,"Ballard Power Systems, Inc. (BLDP)",BLDP
                    NASDAQ Equity,BancFirst Corporation (BANF),BANF
                    NASDAQ Equity,BancFirst Corporation (BANFP),BANFP
                    NASDAQ Equity,"Bancorp 34, Inc. (BCTF)",BCTF
                    NASDAQ Equity,Bandwidth Inc. (BAND),BAND
                    NASDAQ Equity,Bank First National Corporation (BFC),BFC
                    NASDAQ Equity,Bank of Commerce Holdings (CA) (BOCH),BOCH
                    NASDAQ Equity,Bank of Marin Bancorp (BMRC),BMRC
                    NASDAQ Equity,Bank Of Montreal (BMLP),BMLP
                    NASDAQ Equity,Bank of South Carolina Corp. (BKSC),BKSC
                    NASDAQ Equity,"Bank of the James Financial Group, Inc. (BOTJ)",BOTJ
                    NASDAQ Equity,Bank OZK (OZK),OZK
                    NASDAQ Equity,Bank7 Corp. (BSVN),BSVN
                    NASDAQ Equity,BankFinancial Corporation (BFIN),BFIN
                    NASDAQ Equity,"Bankwell Financial Group, Inc. (BWFG)",BWFG
                    NASDAQ Equity,Banner Corporation (BANR),BANR
                    NASDAQ Equity,Baozun Inc. (BZUN),BZUN
                    NASDAQ Equity,Barclays PLC (DFVL),DFVL
                    NASDAQ Equity,Barclays PLC (DFVS),DFVS
                    NASDAQ Equity,Barclays PLC (DLBS),DLBS
                    NASDAQ Equity,Barclays PLC (DTUL),DTUL
                    NASDAQ Equity,Barclays PLC (DTUS),DTUS
                    NASDAQ Equity,Barclays PLC (DTYL),DTYL
                    NASDAQ Equity,Barclays PLC (DTYS),DTYS
                    NASDAQ Equity,Barclays PLC (FLAT),FLAT
                    NASDAQ Equity,Barclays PLC (STPP),STPP
                    NASDAQ Equity,Barclays PLC (TAPR),TAPR
                    NASDAQ Equity,"Barrett Business Services, Inc. (BBSI)",BBSI
                    NASDAQ Equity,Barrick Gold Corporation (GOLD),GOLD
                    NASDAQ Equity,"Bassett Furniture Industries, Incorporated (BSET)",BSET
                    NASDAQ Equity,"Bat Group, Inc. (GLG)",GLG
                    NASDAQ Equity,BATS BZX Exchange (ZTEST),ZTEST
                    NASDAQ Equity,BayCom Corp (BCML),BCML
                    NASDAQ Equity,"BCB Bancorp, Inc. (NJ) (BCBP)",BCBP
                    NASDAQ Equity,"Beacon Roofing Supply, Inc. (BECN)",BECN
                    NASDAQ Equity,"Beasley Broadcast Group, Inc. (BBGI)",BBGI
                    NASDAQ Equity,Bed Bath & Beyond Inc. (BBBY),BBBY
                    NASDAQ Equity,"BeiGene, Ltd. (BGNE)",BGNE
                    NASDAQ Equity,Bel Fuse Inc. (BELFA),BELFA
                    NASDAQ Equity,Bel Fuse Inc. (BELFB),BELFB
                    NASDAQ Equity,"Bellerophon Therapeutics, Inc. (BLPH)",BLPH
                    NASDAQ Equity,"Bellicum Pharmaceuticals, Inc. (BLCM)",BLCM
                    NASDAQ Equity,"Benefitfocus, Inc. (BNFT)",BNFT
                    NASDAQ Equity,Benitec Biopharma Limited (BNTC),BNTC
                    NASDAQ Equity,Benitec Biopharma Limited (BNTCW),BNTCW
                    NASDAQ Equity,Berry Petroleum Corporation (BRY),BRY
                    NASDAQ Equity,"Beyond Meat, Inc. (BYND)",BYND
                    NASDAQ Equity,"BeyondSpring, Inc. (BYSI)",BYSI
                    NASDAQ Equity,"BGC Partners, Inc. (BGCP)",BGCP
                    NASDAQ Equity,Bicycle Therapeutics plc (BCYC),BCYC
                    NASDAQ Equity,Big 5 Sporting Goods Corporation (BGFV),BGFV
                    NASDAQ Equity,Big Rock Partners Acquisition Corp. (BRPA),BRPA
                    NASDAQ Equity,Big Rock Partners Acquisition Corp. (BRPAR),BRPAR
                    NASDAQ Equity,Big Rock Partners Acquisition Corp. (BRPAU),BRPAU
                    NASDAQ Equity,Big Rock Partners Acquisition Corp. (BRPAW),BRPAW
                    NASDAQ Equity,Bilibili Inc. (BILI),BILI
                    NASDAQ Equity,"Bioanalytical Systems, Inc. (BASI)",BASI
                    NASDAQ Equity,"Biocept, Inc. (BIOC)",BIOC
                    NASDAQ Equity,"BioCryst Pharmaceuticals, Inc. (BCRX)",BCRX
                    NASDAQ Equity,"BioDelivery Sciences International, Inc. (BDSI)",BDSI
                    NASDAQ Equity,Biofrontera AG (BFRA),BFRA
                    NASDAQ Equity,Biogen Inc. (BIIB),BIIB
                    NASDAQ Equity,"BioHiTech Global, Inc. (BHTG)",BHTG
                    NASDAQ Equity,"BIO-key International, Inc. (BKYI)",BKYI
                    NASDAQ Equity,"Biolase, Inc. (BIOL)",BIOL
                    NASDAQ Equity,"BioLife Solutions, Inc. (BLFS)",BLFS
                    NASDAQ Equity,BioLineRx Ltd. (BLRX),BLRX
                    NASDAQ Equity,BioMarin Pharmaceutical Inc. (BMRN),BMRN
                    NASDAQ Equity,"Biomerica, Inc. (BMRA)",BMRA
                    NASDAQ Equity,"Bionano Genomics, Inc. (BNGO)",BNGO
                    NASDAQ Equity,"Bionano Genomics, Inc. (BNGOW)",BNGOW
                    NASDAQ Equity,BiondVax Pharmaceuticals Ltd. (BVXV),BVXV
                    NASDAQ Equity,BiondVax Pharmaceuticals Ltd. (BVXVW),BVXVW
                    NASDAQ Equity,"Bio-Path Holdings, Inc. (BPTH)",BPTH
                    NASDAQ Equity,"BioScrip, Inc. (BIOS)",BIOS
                    NASDAQ Equity,"BioSig Technologies, Inc. (BSGM)",BSGM
                    NASDAQ Equity,BioSpecifics Technologies Corp (BSTC),BSTC
                    NASDAQ Equity,Bio-Techne Corp (TECH),TECH
                    NASDAQ Equity,"BioTelemetry, Inc. (BEAT)",BEAT
                    NASDAQ Equity,"BioXcel Therapeutics, Inc. (BTAI)",BTAI
                    NASDAQ Equity,BIQI International Holdings Corporation (BIQI),BIQI
                    NASDAQ Equity,"BJ&#39;s Restaurants, Inc. (BJRI)",BJRI
                    NASDAQ Equity,Black Ridge Acquisition Corp. (BRAC),BRAC
                    NASDAQ Equity,Black Ridge Acquisition Corp. (BRACR),BRACR
                    NASDAQ Equity,Black Ridge Acquisition Corp. (BRACU),BRACU
                    NASDAQ Equity,Black Ridge Acquisition Corp. (BRACW),BRACW
                    NASDAQ Equity,"Blackbaud, Inc. (BLKB)",BLKB
                    NASDAQ Equity,"BlackLine, Inc. (BL)",BL
                    NASDAQ Equity,BlackRock Capital Investment Corporation (BKCC),BKCC
                    NASDAQ Equity,BlackRock TCP Capital Corp. (TCPC),TCPC
                    NASDAQ Equity,Blink Charging Co. (BLNK),BLNK
                    NASDAQ Equity,Blink Charging Co. (BLNKW),BLNKW
                    NASDAQ Equity,"Bloomin&#39; Brands, Inc. (BLMN)",BLMN
                    NASDAQ Equity,"Blucora, Inc. (BCOR)",BCOR
                    NASDAQ Equity,Blue Bird Corporation (BLBD),BLBD
                    NASDAQ Equity,"bluebird bio, Inc. (BLUE)",BLUE
                    NASDAQ Equity,"Blueknight Energy Partners L.P., L.L.C. (BKEP)",BKEP
                    NASDAQ Equity,"Blueknight Energy Partners L.P., L.L.C. (BKEPP)",BKEPP
                    NASDAQ Equity,Blueprint Medicines Corporation (BPMC),BPMC
                    NASDAQ Equity,BlueStar Israel Technology ETF (ITEQ),ITEQ
                    NASDAQ Equity,"BMC Stock Holdings, Inc. (BMCH)",BMCH
                    NASDAQ Equity,"Boingo Wireless, Inc. (WIFI)",WIFI
                    NASDAQ Equity,BOK Financial Corporation (BOKF),BOKF
                    NASDAQ Equity,BOK Financial Corporation (BOKFL),BOKFL
                    NASDAQ Equity,"Bonso Electronics International, Inc. (BNSO)",BNSO
                    NASDAQ Equity,Booking Holdings Inc. (BKNG),BKNG
                    NASDAQ Equity,"Borqs Technologies, Inc.  (BRQS)",BRQS
                    NASDAQ Equity,Boston Omaha Corporation (BOMN),BOMN
                    NASDAQ Equity,"Boston Private Financial Holdings, Inc. (BPFH)",BPFH
                    NASDAQ Equity,"Bottomline Technologies, Inc. (EPAY)",EPAY
                    NASDAQ Equity,Boxlight Corporation (BOXL),BOXL
                    NASDAQ Equity,Boxwood Merger Corp. (BWMC),BWMC
                    NASDAQ Equity,Boxwood Merger Corp. (BWMCU),BWMCU
                    NASDAQ Equity,Boxwood Merger Corp. (BWMCW),BWMCW
                    NASDAQ Equity,Brainstorm Cell Therapeutics Inc. (BCLI),BCLI
                    NASDAQ Equity,Brainsway Ltd. (BWAY),BWAY
                    NASDAQ Equity,Brandes Investment Trust (BVNSC),BVNSC
                    NASDAQ Equity,"Bridge Bancorp, Inc. (BDGE)",BDGE
                    NASDAQ Equity,"Bridgeline Digital, Inc. (BLIN          )",BLIN          
                    NASDAQ Equity,"Bridgewater Bancshares, Inc. (BWB)",BWB
                    NASDAQ Equity,Bridgford Foods Corporation (BRID),BRID
                    NASDAQ Equity,Brightcove Inc. (BCOV),BCOV
                    NASDAQ Equity,"Brighthouse Financial, Inc. (BHF)",BHF
                    NASDAQ Equity,"Brighthouse Financial, Inc. (BHFAL)",BHFAL
                    NASDAQ Equity,"Brighthouse Financial, Inc. (BHFAP)",BHFAP
                    NASDAQ Equity,Broadcom Inc. (AVGO),AVGO
                    NASDAQ Equity,"BroadVision, Inc. (BVSN)",BVSN
                    NASDAQ Equity,Broadway Financial Corporation (BYFC),BYFC
                    NASDAQ Equity,"Broadwind Energy, Inc. (BWEN)",BWEN
                    NASDAQ Equity,Brookfield Property Partners L.P. (BPY),BPY
                    NASDAQ Equity,Brookfield Property Partners L.P. (BPYPP),BPYPP
                    NASDAQ Equity,Brookfield Property REIT Inc. (BPR),BPR
                    NASDAQ Equity,Brookfield Property REIT Inc. (BPRAP),BPRAP
                    NASDAQ Equity,"Brookline Bancorp, Inc. (BRKL)",BRKL
                    NASDAQ Equity,"Brooks Automation, Inc. (BRKS)",BRKS
                    NASDAQ Equity,BRP Inc. (DOOO),DOOO
                    NASDAQ Equity,Bruker Corporation (BRKR),BRKR
                    NASDAQ Equity,Bryn Mawr Bank Corporation (BMTC),BMTC
                    NASDAQ Equity,BSQUARE Corporation (BSQR),BSQR
                    NASDAQ Equity,"Builders FirstSource, Inc. (BLDR)",BLDR
                    NASDAQ Equity,"Business First Bancshares, Inc. (BFST)",BFST
                    NASDAQ Equity,C&F Financial Corporation (CFFI),CFFI
                    NASDAQ Equity,"C.H. Robinson Worldwide, Inc. (CHRW)",CHRW
                    NASDAQ Equity,Cabot Microelectronics Corporation (CCMP),CCMP
                    NASDAQ Equity,"Cadence Design Systems, Inc. (CDNS)",CDNS
                    NASDAQ Equity,"Cadiz, Inc. (CDZI)",CDZI
                    NASDAQ Equity,Caesars Entertainment Corporation (CZR),CZR
                    NASDAQ Equity,Caesarstone Ltd. (CSTE),CSTE
                    NASDAQ Equity,"Caladrius Biosciences, Inc. (CLBS)",CLBS
                    NASDAQ Equity,Calamos Convertible and High Income Fund (CHY),CHY
                    NASDAQ Equity,Calamos Convertible Opportunities and Income Fund (CHI),CHI
                    NASDAQ Equity,Calamos Dynamic Convertible & Income Fund (CCD),CCD
                    NASDAQ Equity,Calamos Global Dynamic Income Fund (CHW),CHW
                    NASDAQ Equity,Calamos Global Total Return Fund (CGO),CGO
                    NASDAQ Equity,Calamos Strategic Total Return Fund (CSQ),CSQ
                    NASDAQ Equity,CalAmp Corp. (CAMP),CAMP
                    NASDAQ Equity,"Calavo Growers, Inc. (CVGW)",CVGW
                    NASDAQ Equity,"Calithera Biosciences, Inc. (CALA)",CALA
                    NASDAQ Equity,"Cal-Maine Foods, Inc. (CALM)",CALM
                    NASDAQ Equity,"Calumet Specialty Products Partners, L.P. (CLMT)",CLMT
                    NASDAQ Equity,Calvert Management Series (CRUSC),CRUSC
                    NASDAQ Equity,"Calyxt, Inc. (CLXT)",CLXT
                    NASDAQ Equity,Cambridge Bancorp (CATC),CATC
                    NASDAQ Equity,Camden National Corporation (CAC),CAC
                    NASDAQ Equity,Camtek Ltd. (CAMT),CAMT
                    NASDAQ Equity,Canadian Solar Inc. (CSIQ),CSIQ
                    NASDAQ Equity,"Cancer Genetics, Inc. (CGIX)",CGIX
                    NASDAQ Equity,Canterbury Park Holding Corporation (CPHC),CPHC
                    NASDAQ Equity,"Capital Bancorp, Inc. (CBNK)",CBNK
                    NASDAQ Equity,Capital City Bank Group (CCBG),CCBG
                    NASDAQ Equity,Capital Product Partners L.P. (CPLP),CPLP
                    NASDAQ Equity,Capital Southwest Corporation (CSWC),CSWC
                    NASDAQ Equity,Capital Southwest Corporation (CSWCL),CSWCL
                    NASDAQ Equity,Capitala Finance Corp. (CPTA),CPTA
                    NASDAQ Equity,Capitala Finance Corp. (CPTAG),CPTAG
                    NASDAQ Equity,Capitala Finance Corp. (CPTAL),CPTAL
                    NASDAQ Equity,"Capitol Federal Financial, Inc. (CFFN)",CFFN
                    NASDAQ Equity,"Capricor Therapeutics, Inc. (CAPR)",CAPR
                    NASDAQ Equity,"CapStar Financial Holdings, Inc. (CSTR)",CSTR
                    NASDAQ Equity,Capstone Turbine Corporation (CPST),CPST
                    NASDAQ Equity,"Cara Therapeutics, Inc. (CARA)",CARA
                    NASDAQ Equity,"Carbon Black, Inc. (CBLK)",CBLK
                    NASDAQ Equity,"Carbonite, Inc. (CARB)",CARB
                    NASDAQ Equity,"Cardiovascular Systems, Inc. (CSII)",CSII
                    NASDAQ Equity,"Cardlytics, Inc. (CDLX)",CDLX
                    NASDAQ Equity,Cardtronics plc (CATM),CATM
                    NASDAQ Equity,"CareDx, Inc. (CDNA)",CDNA
                    NASDAQ Equity,Career Education Corporation (CECO),CECO
                    NASDAQ Equity,"CareTrust REIT, Inc. (CTRE)",CTRE
                    NASDAQ Equity,"CarGurus, Inc. (CARG)",CARG
                    NASDAQ Equity,Carolina Financial Corporation (CARO),CARO
                    NASDAQ Equity,"Carolina Trust BancShares, Inc. (CART)",CART
                    NASDAQ Equity,"Carrizo Oil & Gas, Inc. (CRZO)",CRZO
                    NASDAQ Equity,"Carrols Restaurant Group, Inc. (TAST)",TAST
                    NASDAQ Equity,Carter Bank & Trust (CARE),CARE
                    NASDAQ Equity,"Carver Bancorp, Inc. (CARV)",CARV
                    NASDAQ Equity,"Casa Systems, Inc. (CASA)",CASA
                    NASDAQ Equity,"Casella Waste Systems, Inc. (CWST)",CWST
                    NASDAQ Equity,"Caseys General Stores, Inc. (CASY)",CASY
                    NASDAQ Equity,"CASI Pharmaceuticals, Inc. (CASI)",CASI
                    NASDAQ Equity,"Cass Information Systems, Inc (CASS)",CASS
                    NASDAQ Equity,"Cassava Sciences, Inc. (SAVA)",SAVA
                    NASDAQ Equity,Castor Maritime Inc. (CTRM),CTRM
                    NASDAQ Equity,"Catabasis Pharmaceuticals, Inc. (CATB)",CATB
                    NASDAQ Equity,"Catalyst Biosciences, Inc.  (CBIO)",CBIO
                    NASDAQ Equity,"Catalyst Pharmaceuticals, Inc. (CPRX)",CPRX
                    NASDAQ Equity,"Catasys, Inc. (CATS)",CATS
                    NASDAQ Equity,Cathay General Bancorp (CATY),CATY
                    NASDAQ Equity,"Cavco Industries, Inc. (CVCO)",CVCO
                    NASDAQ Equity,"CB Financial Services, Inc. (CBFV)",CBFV
                    NASDAQ Equity,"CBAK Energy Technology, Inc. (CBAT)",CBAT
                    NASDAQ Equity,"CBM Bancorp, Inc. (CBMB)",CBMB
                    NASDAQ Equity,"Cboe Global Markets, Inc. (CBOE)",CBOE
                    NASDAQ Equity,"CBTX, Inc. (CBTX)",CBTX
                    NASDAQ Equity,"CDK Global, Inc. (CDK)",CDK
                    NASDAQ Equity,CDW Corporation (CDW),CDW
                    NASDAQ Equity,CECO Environmental Corp. (CECE),CECE
                    NASDAQ Equity,Celcuity Inc. (CELC),CELC
                    NASDAQ Equity,Celgene Corporation (CELG),CELG
                    NASDAQ Equity,Celgene Corporation (CELGZ),CELGZ
                    NASDAQ Equity,"Celldex Therapeutics, Inc. (CLDX)",CLDX
                    NASDAQ Equity,Cellect Biotechnology Ltd. (APOP),APOP
                    NASDAQ Equity,Cellect Biotechnology Ltd. (APOPW),APOPW
                    NASDAQ Equity,"Cellectar Biosciences, Inc. (CLRB)",CLRB
                    NASDAQ Equity,"Cellectar Biosciences, Inc. (CLRBW)",CLRBW
                    NASDAQ Equity,"Cellectar Biosciences, Inc. (CLRBZ)",CLRBZ
                    NASDAQ Equity,Cellectis S.A. (CLLS),CLLS
                    NASDAQ Equity,"Cellular Biomedicine Group, Inc. (CBMG)",CBMG
                    NASDAQ Equity,Celsion Corporation (CLSN),CLSN
                    NASDAQ Equity,"Celsius Holdings, Inc. (CELH)",CELH
                    NASDAQ Equity,Celyad SA (CYAD),CYAD
                    NASDAQ Equity,Cemtrex Inc. (CETX),CETX
                    NASDAQ Equity,Cemtrex Inc. (CETXP),CETXP
                    NASDAQ Equity,Cemtrex Inc. (CETXW),CETXW
                    NASDAQ Equity,"Centennial Resource Development, Inc. (CDEV)",CDEV
                    NASDAQ Equity,CenterState Bank Corporation (CSFL),CSFL
                    NASDAQ Equity,Central European Media Enterprises Ltd. (CETV),CETV
                    NASDAQ Equity,Central Federal Corporation (CFBK),CFBK
                    NASDAQ Equity,Central Garden & Pet Company (CENT),CENT
                    NASDAQ Equity,Central Garden & Pet Company (CENTA),CENTA
                    NASDAQ Equity,Central Valley Community Bancorp (CVCY),CVCY
                    NASDAQ Equity,Centric Brands Inc. (CTRC),CTRC
                    NASDAQ Equity,Century Aluminum Company (CENX),CENX
                    NASDAQ Equity,"Century Bancorp, Inc. (CNBKA)",CNBKA
                    NASDAQ Equity,"Century Casinos, Inc. (CNTY)",CNTY
                    NASDAQ Equity,Ceragon Networks Ltd. (CRNT),CRNT
                    NASDAQ Equity,Cerecor Inc. (CERC),CERC
                    NASDAQ Equity,Cerner Corporation (CERN),CERN
                    NASDAQ Equity,Cerus Corporation (CERS),CERS
                    NASDAQ Equity,Cesca Therapeutics Inc. (KOOL),KOOL
                    NASDAQ Equity,"CEVA, Inc. (CEVA)",CEVA
                    NASDAQ Equity,CF Finance Acquisition Corp. (CFFA),CFFA
                    NASDAQ Equity,CF Finance Acquisition Corp. (CFFAU),CFFAU
                    NASDAQ Equity,CF Finance Acquisition Corp. (CFFAW),CFFAW
                    NASDAQ Equity,"Champions Oncology, Inc. (CSBR)",CSBR
                    NASDAQ Equity,Changyou.com Limited (CYOU),CYOU
                    NASDAQ Equity,"Chanticleer Holdings, Inc. (BURG)",BURG
                    NASDAQ Equity,Charles & Colvard Ltd. (CTHR),CTHR
                    NASDAQ Equity,"Chart Industries, Inc. (GTLS)",GTLS
                    NASDAQ Equity,"Charter Communications, Inc. (CHTR)",CHTR
                    NASDAQ Equity,ChaSerg Technology Acquisition Corp. (CTAC),CTAC
                    NASDAQ Equity,ChaSerg Technology Acquisition Corp. (CTACU),CTACU
                    NASDAQ Equity,ChaSerg Technology Acquisition Corp. (CTACW),CTACW
                    NASDAQ Equity,Check Point Software Technologies Ltd. (CHKP),CHKP
                    NASDAQ Equity,Check-Cap Ltd. (CHEK),CHEK
                    NASDAQ Equity,Check-Cap Ltd. (CHEKW),CHEKW
                    NASDAQ Equity,Check-Cap Ltd. (CHEKZ),CHEKZ
                    NASDAQ Equity,"Checkpoint Therapeutics, Inc. (CKPT)",CKPT
                    NASDAQ Equity,"Chembio Diagnostics, Inc. (CEMI)",CEMI
                    NASDAQ Equity,Chemical Financial Corporation (CHFC),CHFC
                    NASDAQ Equity,"ChemoCentryx, Inc. (CCXI)",CCXI
                    NASDAQ Equity,Chemung Financial Corp (CHMG),CHMG
                    NASDAQ Equity,Cherokee Inc. (CHKE),CHKE
                    NASDAQ Equity,"CHF Solutions, Inc. (CHFS)",CHFS
                    NASDAQ Equity,"Chiasma, Inc. (CHMA)",CHMA
                    NASDAQ Equity,"Chicken Soup for the Soul Entertainment, Inc. (CSSE)",CSSE
                    NASDAQ Equity,"Chicken Soup for the Soul Entertainment, Inc. (CSSEP)",CSSEP
                    NASDAQ Equity,"Children&#39;s Place, Inc. (The) (PLCE)",PLCE
                    NASDAQ Equity,"Chimerix, Inc. (CMRX)",CMRX
                    NASDAQ Equity,"China Advanced Construction Materials Group, Inc. (CADC)",CADC
                    NASDAQ Equity,"China Automotive Systems, Inc. (CAAS)",CAAS
                    NASDAQ Equity,"China Biologic Products Holdings, Inc. (CBPO)",CBPO
                    NASDAQ Equity,"China Ceramics Co., Ltd. (CCCL)",CCCL
                    NASDAQ Equity,"China Customer Relations Centers, Inc. (CCRC)",CCRC
                    NASDAQ Equity,China Finance Online Co. Limited (JRJC),JRJC
                    NASDAQ Equity,"China HGS Real Estate, Inc. (HGSH)",HGSH
                    NASDAQ Equity,China Index Holdings Limited (CIH),CIH
                    NASDAQ Equity,China Internet Nationwide Financial Services Inc. (CIFS),CIFS
                    NASDAQ Equity,"China Jo-Jo Drugstores, Inc. (CJJD)",CJJD
                    NASDAQ Equity,China Lending Corporation (CLDC),CLDC
                    NASDAQ Equity,"China Natural Resources, Inc. (CHNR)",CHNR
                    NASDAQ Equity,China Recycling Energy Corporation (CREG),CREG
                    NASDAQ Equity,"China SXT Pharmaceuticals, Inc. (SXTC)",SXTC
                    NASDAQ Equity,China TechFaith Wireless Communication Technology Limited (CNTF),CNTF
                    NASDAQ Equity,China XD Plastics Company Limited (CXDC),CXDC
                    NASDAQ Equity,ChinaCache International Holdings Ltd. (CCIH),CCIH
                    NASDAQ Equity,"ChinaNet Online Holdings, Inc. (CNET)",CNET
                    NASDAQ Equity,ChipMOS TECHNOLOGIES INC. (IMOS),IMOS
                    NASDAQ Equity,ChromaDex Corporation (CDXC),CDXC
                    NASDAQ Equity,CHS Inc (CHSCL),CHSCL
                    NASDAQ Equity,CHS Inc (CHSCM),CHSCM
                    NASDAQ Equity,CHS Inc (CHSCN),CHSCN
                    NASDAQ Equity,CHS Inc (CHSCO),CHSCO
                    NASDAQ Equity,CHS Inc (CHSCP),CHSCP
                    NASDAQ Equity,"Churchill Downs, Incorporated (CHDN)",CHDN
                    NASDAQ Equity,"Chuy&#39;s Holdings, Inc. (CHUY)",CHUY
                    NASDAQ Equity,"Cidara Therapeutics, Inc. (CDTX)",CDTX
                    NASDAQ Equity,CIM Commercial Trust Corporation (CMCT),CMCT
                    NASDAQ Equity,CIM Commercial Trust Corporation (CMCTP),CMCTP
                    NASDAQ Equity,Cimpress N.V (CMPR),CMPR
                    NASDAQ Equity,Cincinnati Financial Corporation (CINF),CINF
                    NASDAQ Equity,Cinedigm Corp (CIDM),CIDM
                    NASDAQ Equity,Cintas Corporation (CTAS),CTAS
                    NASDAQ Equity,"Cirrus Logic, Inc. (CRUS)",CRUS
                    NASDAQ Equity,"Cisco Systems, Inc. (CSCO)",CSCO
                    NASDAQ Equity,"Citi Trends, Inc. (CTRN)",CTRN
                    NASDAQ Equity,"Citius Pharmaceuticals, Inc. (CTXR)",CTXR
                    NASDAQ Equity,"Citius Pharmaceuticals, Inc. (CTXRW)",CTXRW
                    NASDAQ Equity,Citizens & Northern Corp (CZNC),CZNC
                    NASDAQ Equity,"Citizens Community Bancorp, Inc. (CZWI)",CZWI
                    NASDAQ Equity,Citizens First Corporation (CZFC),CZFC
                    NASDAQ Equity,Citizens Holding Company (CIZN),CIZN
                    NASDAQ Equity,"Citrix Systems, Inc. (CTXS)",CTXS
                    NASDAQ Equity,City Holding Company (CHCO),CHCO
                    NASDAQ Equity,"Civista Bancshares, Inc.  (CIVB)",CIVB
                    NASDAQ Equity,"Civista Bancshares, Inc.  (CIVBP)",CIVBP
                    NASDAQ Equity,Clarus Corporation (CLAR),CLAR
                    NASDAQ Equity,Clean Energy Fuels Corp. (CLNE),CLNE
                    NASDAQ Equity,ClearBridge All Cap Growth ETF (CACG),CACG
                    NASDAQ Equity,ClearBridge Dividend Strategy ESG ETF (YLDE),YLDE
                    NASDAQ Equity,ClearBridge Large Cap Growth ESG ETF (LRGE),LRGE
                    NASDAQ Equity,"Clearfield, Inc. (CLFD)",CLFD
                    NASDAQ Equity,"ClearOne, Inc. (CLRO)",CLRO
                    NASDAQ Equity,"Clearside Biomedical, Inc. (CLSD)",CLSD
                    NASDAQ Equity,ClearSign Combustion Corporation (CLIR),CLIR
                    NASDAQ Equity,"Cleveland BioLabs, Inc. (CBLI)",CBLI
                    NASDAQ Equity,"Clovis Oncology, Inc. (CLVS)",CLVS
                    NASDAQ Equity,CLPS Incorporation (CLPS),CLPS
                    NASDAQ Equity,CM Finance Inc (CMFN),CMFN
                    NASDAQ Equity,CM Finance Inc (CMFNL),CMFNL
                    NASDAQ Equity,CME Group Inc. (CME),CME
                    NASDAQ Equity,CNB Financial Corporation (CCNE),CCNE
                    NASDAQ Equity,Coastal Financial Corporation (CCB),CCB
                    NASDAQ Equity,"Coca-Cola Consolidated, Inc. (COKE)",COKE
                    NASDAQ Equity,"Cocrystal Pharma, Inc. (COCP)",COCP
                    NASDAQ Equity,"Coda Octopus Group, Inc. (CODA)",CODA
                    NASDAQ Equity,"Codexis, Inc. (CDXS)",CDXS
                    NASDAQ Equity,"Co-Diagnostics, Inc. (CODX)",CODX
                    NASDAQ Equity,"Codorus Valley Bancorp, Inc (CVLY)",CVLY
                    NASDAQ Equity,"Coffee Holding Co., Inc. (JVA)",JVA
                    NASDAQ Equity,"Cogent Communications Holdings, Inc. (CCOI)",CCOI
                    NASDAQ Equity,Cognex Corporation (CGNX),CGNX
                    NASDAQ Equity,Cognizant Technology Solutions Corporation (CTSH),CTSH
                    NASDAQ Equity,"CohBar, Inc. (CWBR)",CWBR
                    NASDAQ Equity,"Coherent, Inc. (COHR)",COHR
                    NASDAQ Equity,"Coherus BioSciences, Inc. (CHRS)",CHRS
                    NASDAQ Equity,"Cohu, Inc. (COHU)",COHU
                    NASDAQ Equity,"Collectors Universe, Inc. (CLCT)",CLCT
                    NASDAQ Equity,"Collegium Pharmaceutical, Inc. (COLL)",COLL
                    NASDAQ Equity,Colliers International Group Inc.  (CIGI),CIGI
                    NASDAQ Equity,CollPlant Biotechnologies Ltd. (CLGN),CLGN
                    NASDAQ Equity,"Colony Bankcorp, Inc. (CBAN)",CBAN
                    NASDAQ Equity,"Columbia Banking System, Inc. (COLB)",COLB
                    NASDAQ Equity,"Columbia Financial, Inc. (CLBK)",CLBK
                    NASDAQ Equity,Columbia Sportswear Company (COLM),COLM
                    NASDAQ Equity,Columbus McKinnon Corporation (CMCO),CMCO
                    NASDAQ Equity,Comcast Corporation (CMCSA),CMCSA
                    NASDAQ Equity,"Command Center, Inc. (CCNI)",CCNI
                    NASDAQ Equity,"Commerce Bancshares, Inc. (CBSH)",CBSH
                    NASDAQ Equity,"Commerce Bancshares, Inc. (CBSHP)",CBSHP
                    NASDAQ Equity,"Commercial Vehicle Group, Inc. (CVGI)",CVGI
                    NASDAQ Equity,"CommScope Holding Company, Inc. (COMM)",COMM
                    NASDAQ Equity,"Communications Systems, Inc. (JCS)",JCS
                    NASDAQ Equity,Community Bankers Trust Corporation. (ESXB),ESXB
                    NASDAQ Equity,"Community First Bancshares, Inc. (CFBI)",CFBI
                    NASDAQ Equity,"Community Trust Bancorp, Inc. (CTBI)",CTBI
                    NASDAQ Equity,Community West Bancshares (CWBC),CWBC
                    NASDAQ Equity,"Commvault Systems, Inc. (CVLT)",CVLT
                    NASDAQ Equity,Compugen Ltd. (CGEN),CGEN
                    NASDAQ Equity,"Computer Programs and Systems, Inc. (CPSI)",CPSI
                    NASDAQ Equity,"Computer Task Group, Incorporated (CTG)",CTG
                    NASDAQ Equity,"comScore, Inc. (SCOR)",SCOR
                    NASDAQ Equity,"Comstock Holding Companies, Inc. (CHCI)",CHCI
                    NASDAQ Equity,Comtech Telecommunications Corp. (CMTL),CMTL
                    NASDAQ Equity,Conatus Pharmaceuticals Inc. (CNAT),CNAT
                    NASDAQ Equity,"Concert Pharmaceuticals, Inc. (CNCE)",CNCE
                    NASDAQ Equity,"Concrete Pumping Holdings, Inc.  (BBCP)",BBCP
                    NASDAQ Equity,"Condor Hospitality Trust, Inc. (CDOR)",CDOR
                    NASDAQ Equity,"ConforMIS, Inc. (CFMS)",CFMS
                    NASDAQ Equity,"Conifer Holdings, Inc. (CNFR)",CNFR
                    NASDAQ Equity,"Conifer Holdings, Inc. (CNFRL)",CNFRL
                    NASDAQ Equity,CONMED Corporation (CNMD),CNMD
                    NASDAQ Equity,"Connecticut Water Service, Inc. (CTWS)",CTWS
                    NASDAQ Equity,"ConnectOne Bancorp, Inc. (CNOB)",CNOB
                    NASDAQ Equity,"Conn&#39;s, Inc. (CONN)",CONN
                    NASDAQ Equity,"Consolidated Communications Holdings, Inc. (CNSL)",CNSL
                    NASDAQ Equity,Consolidated Water Co. Ltd. (CWCO),CWCO
                    NASDAQ Equity,Constellation Alpha Capital Corp. (CNAC),CNAC
                    NASDAQ Equity,Constellation Alpha Capital Corp. (CNACR),CNACR
                    NASDAQ Equity,Constellation Alpha Capital Corp. (CNACU),CNACU
                    NASDAQ Equity,Constellation Alpha Capital Corp. (CNACW),CNACW
                    NASDAQ Equity,"Constellation Pharmaceuticals, Inc. (CNST)",CNST
                    NASDAQ Equity,"Construction Partners, Inc. (ROAD)",ROAD
                    NASDAQ Equity,"Consumer Portfolio Services, Inc. (CPSS)",CPSS
                    NASDAQ Equity,ContraFect Corporation (CFRX),CFRX
                    NASDAQ Equity,ContraVir Pharmaceuticals Inc. (CTRV),CTRV
                    NASDAQ Equity,Control4 Corporation (CTRL),CTRL
                    NASDAQ Equity,Cool Holdings Inc. (AWSM),AWSM
                    NASDAQ Equity,"Copart, Inc. (CPRT)",CPRT
                    NASDAQ Equity,"Corbus Pharmaceuticals Holdings, Inc. (CRBP)",CRBP
                    NASDAQ Equity,Corcept Therapeutics Incorporated (CORT),CORT
                    NASDAQ Equity,"Core-Mark Holding Company, Inc. (CORE)",CORE
                    NASDAQ Equity,"Cornerstone OnDemand, Inc. (CSOD)",CSOD
                    NASDAQ Equity,Correvio Pharma Corp. (CORV),CORV
                    NASDAQ Equity,"Cortexyme, Inc. (CRTX)",CRTX
                    NASDAQ Equity,Cortland Bancorp (CLDB),CLDB
                    NASDAQ Equity,CorVel Corp. (CRVL),CRVL
                    NASDAQ Equity,"Corvus Pharmaceuticals, Inc. (CRVS)",CRVS
                    NASDAQ Equity,"CoStar Group, Inc. (CSGP)",CSGP
                    NASDAQ Equity,Costco Wholesale Corporation (COST),COST
                    NASDAQ Equity,CounterPath Corporation (CPAH),CPAH
                    NASDAQ Equity,"County Bancorp, Inc. (ICBK)",ICBK
                    NASDAQ Equity,Coupa Software Incorporated (COUP),COUP
                    NASDAQ Equity,"Covenant Transportation Group, Inc. (CVTI)",CVTI
                    NASDAQ Equity,"Covetrus, Inc. (CVET)",CVET
                    NASDAQ Equity,Cowen Inc. (COWN),COWN
                    NASDAQ Equity,Cowen Inc. (COWNL),COWNL
                    NASDAQ Equity,Cowen Inc. (COWNZ),COWNZ
                    NASDAQ Equity,CPI Card Group Inc. (PMTS),PMTS
                    NASDAQ Equity,CPS Technologies Corp. (CPSH),CPSH
                    NASDAQ Equity,"CRA International,Inc. (CRAI)",CRAI
                    NASDAQ Equity,"Cracker Barrel Old Country Store, Inc. (CBRL)",CBRL
                    NASDAQ Equity,"Craft Brew Alliance, Inc. (BREW)",BREW
                    NASDAQ Equity,Cray Inc (CRAY),CRAY
                    NASDAQ Equity,"Creative Realities, Inc. (CREX)",CREX
                    NASDAQ Equity,"Creative Realities, Inc. (CREXW)",CREXW
                    NASDAQ Equity,Credit Acceptance Corporation (CACC),CACC
                    NASDAQ Equity,Credit Suisse AG (DGLD),DGLD
                    NASDAQ Equity,Credit Suisse AG (DSLV),DSLV
                    NASDAQ Equity,Credit Suisse AG (GLDI),GLDI
                    NASDAQ Equity,Credit Suisse AG (SLVO),SLVO
                    NASDAQ Equity,Credit Suisse AG (TVIX),TVIX
                    NASDAQ Equity,Credit Suisse AG (UGLD),UGLD
                    NASDAQ Equity,Credit Suisse AG (USLV),USLV
                    NASDAQ Equity,Credit Suisse AG (USOI),USOI
                    NASDAQ Equity,Credit Suisse AG (VIIX),VIIX
                    NASDAQ Equity,Credit Suisse AG (ZIV),ZIV
                    NASDAQ Equity,"Cree, Inc. (CREE)",CREE
                    NASDAQ Equity,Crescent Acquisition Corp (CRSA),CRSA
                    NASDAQ Equity,Crescent Acquisition Corp (CRSAU),CRSAU
                    NASDAQ Equity,Crescent Acquisition Corp (CRSAW),CRSAW
                    NASDAQ Equity,Cresud S.A.C.I.F. y A. (CRESY),CRESY
                    NASDAQ Equity,"Crinetics Pharmaceuticals, Inc. (CRNX)",CRNX
                    NASDAQ Equity,CRISPR Therapeutics AG (CRSP),CRSP
                    NASDAQ Equity,Criteo S.A. (CRTO),CRTO
                    NASDAQ Equity,"Crocs, Inc. (CROX)",CROX
                    NASDAQ Equity,Cronos Group Inc. (CRON),CRON
                    NASDAQ Equity,"Cross Country Healthcare, Inc. (CCRN)",CCRN
                    NASDAQ Equity,"CrowdStrike Holdings, Inc. (CRWD)",CRWD
                    NASDAQ Equity,"Crown Crafts, Inc. (CRWS)",CRWS
                    NASDAQ Equity,"CryoPort, Inc. (CYRX)",CYRX
                    NASDAQ Equity,"CryoPort, Inc. (CYRXW)",CYRXW
                    NASDAQ Equity,"CSG Systems International, Inc. (CSGS)",CSGS
                    NASDAQ Equity,CSI Compressco LP (CCLP),CCLP
                    NASDAQ Equity,CSP Inc. (CSPI),CSPI
                    NASDAQ Equity,"CSW Industrials, Inc. (CSWI)",CSWI
                    NASDAQ Equity,CSX Corporation (CSX),CSX
                    NASDAQ Equity,CTI BioPharma Corp. (CTIC),CTIC
                    NASDAQ Equity,CTI Industries Corporation (CTIB),CTIB
                    NASDAQ Equity,"Ctrip.com International, Ltd. (CTRP)",CTRP
                    NASDAQ Equity,"Cue Biopharma, Inc. (CUE)",CUE
                    NASDAQ Equity,"CUI Global, Inc. (CUI)",CUI
                    NASDAQ Equity,Cumberland Pharmaceuticals Inc. (CPIX),CPIX
                    NASDAQ Equity,Cumulus Media Inc. (CMLS),CMLS
                    NASDAQ Equity,"Curis, Inc. (CRIS)",CRIS
                    NASDAQ Equity,"Cutera, Inc. (CUTR)",CUTR
                    NASDAQ Equity,CVB Financial Corporation (CVBF),CVBF
                    NASDAQ Equity,CVD Equipment Corporation (CVV),CVV
                    NASDAQ Equity,Cyanotech Corporation (CYAN),CYAN
                    NASDAQ Equity,CyberArk Software Ltd. (CYBR),CYBR
                    NASDAQ Equity,CyberOptics Corporation (CYBE),CYBE
                    NASDAQ Equity,"Cyclacel Pharmaceuticals, Inc. (CYCC)",CYCC
                    NASDAQ Equity,"Cyclacel Pharmaceuticals, Inc. (CYCCP)",CYCCP
                    NASDAQ Equity,"Cyclerion Therapeutics, Inc. (CYCN)",CYCN
                    NASDAQ Equity,CymaBay Therapeutics Inc. (CBAY),CBAY
                    NASDAQ Equity,Cypress Semiconductor Corporation (CY),CY
                    NASDAQ Equity,CYREN Ltd. (CYRN),CYRN
                    NASDAQ Equity,CyrusOne Inc (CONE),CONE
                    NASDAQ Equity,"Cytokinetics, Incorporated (CYTK)",CYTK
                    NASDAQ Equity,"CytomX Therapeutics, Inc. (CTMX)",CTMX
                    NASDAQ Equity,Cytori Therapeutics Inc. (CYTX),CYTX
                    NASDAQ Equity,Cytori Therapeutics Inc. (CYTXZ),CYTXZ
                    NASDAQ Equity,Cytosorbents Corporation (CTSO),CTSO
                    NASDAQ Equity,Daily Journal Corp. (S.C.) (DJCO),DJCO
                    NASDAQ Equity,"Daktronics, Inc. (DAKT)",DAKT
                    NASDAQ Equity,"Dare Bioscience, Inc. (DARE)",DARE
                    NASDAQ Equity,DarioHealth Corp. (DRIO),DRIO
                    NASDAQ Equity,DarioHealth Corp. (DRIOW),DRIOW
                    NASDAQ Equity,"DASAN Zhone Solutions, Inc. (DZSI)",DZSI
                    NASDAQ Equity,"Daseke, Inc. (DSKE)",DSKE
                    NASDAQ Equity,"Daseke, Inc. (DSKEW)",DSKEW
                    NASDAQ Equity,Data I/O Corporation (DAIO),DAIO
                    NASDAQ Equity,Datasea Inc. (DTSS),DTSS
                    NASDAQ Equity,"Dave & Buster&#39;s Entertainment, Inc. (PLAY)",PLAY
                    NASDAQ Equity,DAVIDsTEA Inc. (DTEA),DTEA
                    NASDAQ Equity,Davis Select Financial ETF (DFNL),DFNL
                    NASDAQ Equity,Davis Select International ETF (DINT),DINT
                    NASDAQ Equity,Davis Select U.S. Equity ETF (DUSA),DUSA
                    NASDAQ Equity,Davis Select Worldwide ETF (DWLD),DWLD
                    NASDAQ Equity,Dawson Geophysical Company (DWSN),DWSN
                    NASDAQ Equity,DBV Technologies S.A. (DBVT),DBVT
                    NASDAQ Equity,DD3 Acquisition Corp. (DDMX),DDMX
                    NASDAQ Equity,DD3 Acquisition Corp. (DDMXU),DDMXU
                    NASDAQ Equity,DD3 Acquisition Corp. (DDMXW),DDMXW
                    NASDAQ Equity,"Deciphera Pharmaceuticals, Inc. (DCPH)",DCPH
                    NASDAQ Equity,"Del Frisco&#39;s Restaurant Group, Inc. (DFRG)",DFRG
                    NASDAQ Equity,"Del Taco Restaurants, Inc. (TACO)",TACO
                    NASDAQ Equity,"Del Taco Restaurants, Inc. (TACOW)",TACOW
                    NASDAQ Equity,"DelMar Pharmaceuticals, Inc. (DMPI)",DMPI
                    NASDAQ Equity,Denali Therapeutics Inc. (DNLI),DNLI
                    NASDAQ Equity,Denny&#39;s Corporation (DENN),DENN
                    NASDAQ Equity,DENTSPLY SIRONA Inc. (XRAY),XRAY
                    NASDAQ Equity,"Dermira, Inc. (DERM)",DERM
                    NASDAQ Equity,Destination Maternity Corporation (DEST),DEST
                    NASDAQ Equity,"Destination XL Group, Inc. (DXLG)",DXLG
                    NASDAQ Equity,"Deswell Industries, Inc. (DSWL)",DSWL
                    NASDAQ Equity,"DexCom, Inc. (DXCM)",DXCM
                    NASDAQ Equity,DFB Healthcare Acquisitions Corp. (DFBH),DFBH
                    NASDAQ Equity,DFB Healthcare Acquisitions Corp. (DFBHU),DFBHU
                    NASDAQ Equity,DFB Healthcare Acquisitions Corp. (DFBHW),DFBHW
                    NASDAQ Equity,DHX Media Ltd. (DHXM),DHXM
                    NASDAQ Equity,DiaMedica Therapeutics Inc. (DMAC),DMAC
                    NASDAQ Equity,Diamond Eagle Acquisition Corp. (DEACU),DEACU
                    NASDAQ Equity,"Diamond Hill Investment Group, Inc. (DHIL)",DHIL
                    NASDAQ Equity,"Diamondback Energy, Inc. (FANG)",FANG
                    NASDAQ Equity,DiamondPeak Holdings Corp. (DPHC),DPHC
                    NASDAQ Equity,DiamondPeak Holdings Corp. (DPHCU),DPHCU
                    NASDAQ Equity,DiamondPeak Holdings Corp. (DPHCW),DPHCW
                    NASDAQ Equity,"Dicerna Pharmaceuticals, Inc. (DRNA)",DRNA
                    NASDAQ Equity,Diffusion Pharmaceuticals Inc. (DFFN),DFFN
                    NASDAQ Equity,Digi International Inc. (DGII),DGII
                    NASDAQ Equity,Digimarc Corporation (DMRC),DMRC
                    NASDAQ Equity,Digirad Corporation (DRAD),DRAD
                    NASDAQ Equity,"Digital Ally, Inc. (DGLY)",DGLY
                    NASDAQ Equity,"Digital Turbine, Inc. (APPS)",APPS
                    NASDAQ Equity,"Dime Community Bancshares, Inc. (DCOM)",DCOM
                    NASDAQ Equity,Diodes Incorporated (DIOD),DIOD
                    NASDAQ Equity,"Discovery, Inc. (DISCA)",DISCA
                    NASDAQ Equity,"Discovery, Inc. (DISCB)",DISCB
                    NASDAQ Equity,"Discovery, Inc. (DISCK)",DISCK
                    NASDAQ Equity,DISH Network Corporation (DISH),DISH
                    NASDAQ Equity,Diversicare Healthcare Services Inc. (DVCR),DVCR
                    NASDAQ Equity,"Diversified Restaurant Holdings, Inc. (SAUC)",SAUC
                    NASDAQ Equity,DLH Holdings Corp. (DLHC),DLHC
                    NASDAQ Equity,DMC Global Inc. (BOOM),BOOM
                    NASDAQ Equity,DNB Financial Corp (DNBF),DNBF
                    NASDAQ Equity,"DocuSign, Inc. (DOCU)",DOCU
                    NASDAQ Equity,Dogness (International) Corporation (DOGZ),DOGZ
                    NASDAQ Equity,"Dollar Tree, Inc. (DLTR)",DLTR
                    NASDAQ Equity,"Dolphin Entertainment, Inc. (DLPN)",DLPN
                    NASDAQ Equity,"Dolphin Entertainment, Inc. (DLPNW)",DLPNW
                    NASDAQ Equity,"Domo, Inc. (DOMO)",DOMO
                    NASDAQ Equity,"Donegal Group, Inc. (DGICA)",DGICA
                    NASDAQ Equity,"Donegal Group, Inc. (DGICB)",DGICB
                    NASDAQ Equity,"Dorchester Minerals, L.P. (DMLP)",DMLP
                    NASDAQ Equity,"Dorman Products, Inc. (DORM)",DORM
                    NASDAQ Equity,"Dova Pharmaceuticals, Inc. (DOVA)",DOVA
                    NASDAQ Equity,Dragon Victory International Limited (LYL),LYL
                    NASDAQ Equity,"Dropbox, Inc. (DBX)",DBX
                    NASDAQ Equity,"DropCar, Inc. (DCAR)",DCAR
                    NASDAQ Equity,DryShips Inc. (DRYS),DRYS
                    NASDAQ Equity,"DSP Group, Inc. (DSPG)",DSPG
                    NASDAQ Equity,Duluth Holdings Inc. (DLTH),DLTH
                    NASDAQ Equity,"Dunkin&#39; Brands Group, Inc. (DNKN)",DNKN
                    NASDAQ Equity,DURECT Corporation (DRRX),DRRX
                    NASDAQ Equity,"DXP Enterprises, Inc. (DXPE)",DXPE
                    NASDAQ Equity,"Dyadic International, Inc. (DYAI)",DYAI
                    NASDAQ Equity,Dynasil Corporation of America (DYSL),DYSL
                    NASDAQ Equity,Dynatronics Corporation (DYNT),DYNT
                    NASDAQ Equity,Dynavax Technologies Corporation (DVAX),DVAX
                    NASDAQ Equity,E*TRADE Financial Corporation (ETFC),ETFC
                    NASDAQ Equity,E.W. Scripps Company (The) (SSP),SSP
                    NASDAQ Equity,"Eagle Bancorp Montana, Inc. (EBMT)",EBMT
                    NASDAQ Equity,"Eagle Bancorp, Inc. (EGBN)",EGBN
                    NASDAQ Equity,Eagle Bulk Shipping Inc. (EGLE),EGLE
                    NASDAQ Equity,"Eagle Financial Bancorp, Inc. (EFBI)",EFBI
                    NASDAQ Equity,"Eagle Pharmaceuticals, Inc. (EGRX)",EGRX
                    NASDAQ Equity,"East West Bancorp, Inc. (EWBC)",EWBC
                    NASDAQ Equity,Eastern Company (The) (EML),EML
                    NASDAQ Equity,"Eastside Distilling, Inc. (EAST)",EAST
                    NASDAQ Equity,Eaton Vance NextShares Trust (EVGBC),EVGBC
                    NASDAQ Equity,Eaton Vance NextShares Trust (EVSTC),EVSTC
                    NASDAQ Equity,Eaton Vance NextShares Trust II (EVFTC),EVFTC
                    NASDAQ Equity,Eaton Vance NextShares Trust II (EVLMC),EVLMC
                    NASDAQ Equity,Eaton Vance NextShares Trust II (OKDCC),OKDCC
                    NASDAQ Equity,eBay Inc. (EBAY),EBAY
                    NASDAQ Equity,eBay Inc. (EBAYL),EBAYL
                    NASDAQ Equity,"Ebix, Inc. (EBIX)",EBIX
                    NASDAQ Equity,"Echo Global Logistics, Inc. (ECHO)",ECHO
                    NASDAQ Equity,EchoStar Corporation (SATS),SATS
                    NASDAQ Equity,"Ecology and Environment, Inc. (EEI)",EEI
                    NASDAQ Equity,EDAP TMS S.A. (EDAP),EDAP
                    NASDAQ Equity,"Edesa Biotech, Inc. (EDSA)",EDSA
                    NASDAQ Equity,"Edison Nation, Inc. (EDNT)",EDNT
                    NASDAQ Equity,"Editas Medicine, Inc. (EDIT)",EDIT
                    NASDAQ Equity,EdtechX Holdings Acquisition Corp. (EDTX),EDTX
                    NASDAQ Equity,EdtechX Holdings Acquisition Corp. (EDTXU),EDTXU
                    NASDAQ Equity,EdtechX Holdings Acquisition Corp. (EDTXW),EDTXW
                    NASDAQ Equity,Educational Development Corporation (EDUC),EDUC
                    NASDAQ Equity,eGain Corporation (EGAN),EGAN
                    NASDAQ Equity,"eHealth, Inc. (EHTH)",EHTH
                    NASDAQ Equity,"Eidos Therapeutics, Inc. (EIDX)",EIDX
                    NASDAQ Equity,"Eiger BioPharmaceuticals, Inc. (EIGR)",EIGR
                    NASDAQ Equity,"Ekso Bionics Holdings, Inc. (EKSO)",EKSO
                    NASDAQ Equity,"El Pollo Loco Holdings, Inc. (LOCO)",LOCO
                    NASDAQ Equity,Elbit Systems Ltd. (ESLT),ESLT
                    NASDAQ Equity,"Eldorado Resorts, Inc. (ERI)",ERI
                    NASDAQ Equity,Electrameccanica Vehicles Corp. Ltd. (SOLO),SOLO
                    NASDAQ Equity,Electrameccanica Vehicles Corp. Ltd. (SOLOW),SOLOW
                    NASDAQ Equity,"electroCore, Inc. (ECOR)",ECOR
                    NASDAQ Equity,Electronic Arts Inc. (EA),EA
                    NASDAQ Equity,"Electronics for Imaging, Inc. (EFII)",EFII
                    NASDAQ Equity,"Electro-Sensors, Inc. (ELSE)",ELSE
                    NASDAQ Equity,Elmira Savings Bank NY (The) (ESBK),ESBK
                    NASDAQ Equity,"Eloxx Pharmaceuticals, Inc. (ELOX)",ELOX
                    NASDAQ Equity,Eltek Ltd. (ELTK),ELTK
                    NASDAQ Equity,EMC Insurance Group Inc. (EMCI),EMCI
                    NASDAQ Equity,Emclaire Financial Corp (EMCF),EMCF
                    NASDAQ Equity,EMCORE Corporation (EMKR),EMKR
                    NASDAQ Equity,Emmis Communications Corporation (EMMS),EMMS
                    NASDAQ Equity,"Empire Resorts, Inc. (NYNY)",NYNY
                    NASDAQ Equity,"Enanta Pharmaceuticals, Inc. (ENTA)",ENTA
                    NASDAQ Equity,Encore Capital Group Inc (ECPG),ECPG
                    NASDAQ Equity,Encore Wire Corporation (WIRE),WIRE
                    NASDAQ Equity,Endo International plc (ENDP),ENDP
                    NASDAQ Equity,"Endologix, Inc. (ELGX)",ELGX
                    NASDAQ Equity,ENDRA Life Sciences Inc. (NDRA),NDRA
                    NASDAQ Equity,ENDRA Life Sciences Inc. (NDRAW),NDRAW
                    NASDAQ Equity,"Endurance International Group Holdings, Inc. (EIGI)",EIGI
                    NASDAQ Equity,Energous Corporation (WATT),WATT
                    NASDAQ Equity,"Energy Focus, Inc. (EFOI)",EFOI
                    NASDAQ Equity,"Energy Recovery, Inc. (ERII)",ERII
                    NASDAQ Equity,ENGlobal Corporation (ENG),ENG
                    NASDAQ Equity,Enlivex Therapeutics Ltd. (ENLV),ENLV
                    NASDAQ Equity,"Enochian Biosciences, Inc. (ENOB)",ENOB
                    NASDAQ Equity,"Enphase Energy, Inc. (ENPH)",ENPH
                    NASDAQ Equity,Enstar Group Limited (ESGR),ESGR
                    NASDAQ Equity,Enstar Group Limited (ESGRO),ESGRO
                    NASDAQ Equity,Enstar Group Limited (ESGRP),ESGRP
                    NASDAQ Equity,Entasis Therapeutics Holdings Inc. (ETTX),ETTX
                    NASDAQ Equity,Entegra Financial Corp. (ENFC),ENFC
                    NASDAQ Equity,"Entegris, Inc. (ENTG)",ENTG
                    NASDAQ Equity,Entera Bio Ltd. (ENTX),ENTX
                    NASDAQ Equity,Entera Bio Ltd. (ENTXW),ENTXW
                    NASDAQ Equity,Enterprise Bancorp Inc (EBTC),EBTC
                    NASDAQ Equity,Enterprise Financial Services Corporation (EFSC),EFSC
                    NASDAQ Equity,"Envision Solar International, Inc. (EVSI)",EVSI
                    NASDAQ Equity,"Envision Solar International, Inc. (EVSIW)",EVSIW
                    NASDAQ Equity,"Epizyme, Inc. (EPZM)",EPZM
                    NASDAQ Equity,ePlus inc. (PLUS),PLUS
                    NASDAQ Equity,Epsilon Energy Ltd. (EPSN),EPSN
                    NASDAQ Equity,"Equillium, Inc. (EQ)",EQ
                    NASDAQ Equity,"Equinix, Inc. (EQIX)",EQIX
                    NASDAQ Equity,"Equity Bancshares, Inc. (EQBK)",EQBK
                    NASDAQ Equity,Ericsson (ERIC),ERIC
                    NASDAQ Equity,Erie Indemnity Company (ERIE),ERIE
                    NASDAQ Equity,Erytech Pharma S.A. (ERYP),ERYP
                    NASDAQ Equity,"Escalade, Incorporated (ESCA)",ESCA
                    NASDAQ Equity,"Esperion Therapeutics, Inc. (ESPR)",ESPR
                    NASDAQ Equity,"Esquire Financial Holdings, Inc. (ESQ)",ESQ
                    NASDAQ Equity,"ESSA Bancorp, Inc. (ESSA)",ESSA
                    NASDAQ Equity,ESSA Pharma Inc. (EPIX),EPIX
                    NASDAQ Equity,Establishment Labs Holdings Inc. (ESTA),ESTA
                    NASDAQ Equity,"Estre Ambiental, Inc. (ESTR)",ESTR
                    NASDAQ Equity,"Estre Ambiental, Inc. (ESTRW)",ESTRW
                    NASDAQ Equity,ETF Series Solutions Trust Vident Core U.S. Bond Strategy Fund (VBND),VBND
                    NASDAQ Equity,ETF Series Solutions Trust Vident Core US Equity ETF (VUSE),VUSE
                    NASDAQ Equity,ETF Series Solutions Trust Vident International Equity Fund (VIDI),VIDI
                    NASDAQ Equity,"Eton Pharmaceuticals, Inc. (ETON)",ETON
                    NASDAQ Equity,"Etsy, Inc. (ETSY)",ETSY
                    NASDAQ Equity,Euro Tech Holdings Company Limited (CLWT),CLWT
                    NASDAQ Equity,EuroDry Ltd. (EDRY),EDRY
                    NASDAQ Equity,"Euronet Worldwide, Inc. (EEFT)",EEFT
                    NASDAQ Equity,Euroseas Ltd. (ESEA),ESEA
                    NASDAQ Equity,"Evelo Biosciences, Inc. (EVLO)",EVLO
                    NASDAQ Equity,"Everbridge, Inc. (EVBG)",EVBG
                    NASDAQ Equity,"Ever-Glory International Group, Inc. (EVK)",EVK
                    NASDAQ Equity,"EverQuote, Inc. (EVER)",EVER
                    NASDAQ Equity,"Everspin Technologies, Inc. (MRAM)",MRAM
                    NASDAQ Equity,EVINE Live Inc. (EVLV),EVLV
                    NASDAQ Equity,"EVO Payments, Inc. (EVOP)",EVOP
                    NASDAQ Equity,"Evofem Biosciences, Inc. (EVFM)",EVFM
                    NASDAQ Equity,Evogene Ltd. (EVGN),EVGN
                    NASDAQ Equity,"Evoke Pharma, Inc. (EVOK)",EVOK
                    NASDAQ Equity,"Evolus, Inc. (EOLS)",EOLS
                    NASDAQ Equity,"Evolving Systems, Inc. (EVOL)",EVOL
                    NASDAQ Equity,Exact Sciences Corporation (EXAS),EXAS
                    NASDAQ Equity,Exchange Traded Concepts Trust FLAG-Forensic Accounting Long-S (FLAG),FLAG
                    NASDAQ Equity,Exchange Traded Concepts Trust ROBO Global Robotics and Automa (ROBO),ROBO
                    NASDAQ Equity,"Exela Technologies, Inc. (XELA)",XELA
                    NASDAQ Equity,"Exelixis, Inc. (EXEL)",EXEL
                    NASDAQ Equity,EXFO Inc (EXFO),EXFO
                    NASDAQ Equity,"ExlService Holdings, Inc. (EXLS)",EXLS
                    NASDAQ Equity,"eXp World Holdings, Inc. (EXPI)",EXPI
                    NASDAQ Equity,"Expedia Group, Inc. (EXPE)",EXPE
                    NASDAQ Equity,"Expeditors International of Washington, Inc. (EXPD)",EXPD
                    NASDAQ Equity,"Exponent, Inc. (EXPO)",EXPO
                    NASDAQ Equity,"Extended Stay America, Inc. (STAY)",STAY
                    NASDAQ Equity,"Extraction Oil & Gas, Inc. (XOG)",XOG
                    NASDAQ Equity,"Extreme Networks, Inc. (EXTR)",EXTR
                    NASDAQ Equity,"Eyegate Pharmaceuticals, Inc. (EYEG)",EYEG
                    NASDAQ Equity,"Eyegate Pharmaceuticals, Inc. (EYEGW)",EYEGW
                    NASDAQ Equity,"Eyenovia, Inc. (EYEN)",EYEN
                    NASDAQ Equity,"EyePoint Pharmaceuticals, Inc. (EYPT)",EYPT
                    NASDAQ Equity,"EZCORP, Inc. (EZPW)",EZPW
                    NASDAQ Equity,"F5 Networks, Inc. (FFIV)",FFIV
                    NASDAQ Equity,"Facebook, Inc. (FB)",FB
                    NASDAQ Equity,Falcon Minerals Corporation (FLMN),FLMN
                    NASDAQ Equity,Falcon Minerals Corporation (FLMNW),FLMNW
                    NASDAQ Equity,"Famous Dave&#39;s of America, Inc. (DAVE)",DAVE
                    NASDAQ Equity,Fanhua Inc. (FANH),FANH
                    NASDAQ Equity,Farmer Brothers Company (FARM),FARM
                    NASDAQ Equity,"Farmers & Merchants Bancorp, Inc. (FMAO)",FMAO
                    NASDAQ Equity,Farmers National Banc Corp. (FMNB),FMNB
                    NASDAQ Equity,"FARMMI, INC. (FAMI)",FAMI
                    NASDAQ Equity,"FARO Technologies, Inc. (FARO)",FARO
                    NASDAQ Equity,Fastenal Company (FAST),FAST
                    NASDAQ Equity,FAT Brands Inc. (FAT),FAT
                    NASDAQ Equity,"Fate Therapeutics, Inc. (FATE)",FATE
                    NASDAQ Equity,"Fauquier Bankshares, Inc. (FBSS)",FBSS
                    NASDAQ Equity,FedNat Holding Company (FNHC),FNHC
                    NASDAQ Equity,Fennec Pharmaceuticals Inc. (FENC),FENC
                    NASDAQ Equity,Ferroglobe PLC (GSM),GSM
                    NASDAQ Equity,"FFBW, Inc. (FFBW)",FFBW
                    NASDAQ Equity,Fibrocell Science Inc. (FCSC),FCSC
                    NASDAQ Equity,"FibroGen, Inc (FGEN)",FGEN
                    NASDAQ Equity,"Fidelity D & D Bancorp, Inc. (FDBC)",FDBC
                    NASDAQ Equity,Fidelity Nasdaq Composite Index Tracking Stock (ONEQ),ONEQ
                    NASDAQ Equity,Fidelity Southern Corporation (LION),LION
                    NASDAQ Equity,Fidus Investment Corporation (FDUS),FDUS
                    NASDAQ Equity,Fidus Investment Corporation (FDUSL),FDUSL
                    NASDAQ Equity,Fidus Investment Corporation (FDUSZ),FDUSZ
                    NASDAQ Equity,"Fiesta Restaurant Group, Inc. (FRGI)",FRGI
                    NASDAQ Equity,Fifth Third Bancorp (FITB),FITB
                    NASDAQ Equity,Fifth Third Bancorp (FITBI),FITBI
                    NASDAQ Equity,"Financial Institutions, Inc. (FISI)",FISI
                    NASDAQ Equity,Finisar Corporation (FNSR),FNSR
                    NASDAQ Equity,"Finjan Holdings, Inc. (FNJN)",FNJN
                    NASDAQ Equity,FinTech Acquisition Corp. III (FTAC),FTAC
                    NASDAQ Equity,FinTech Acquisition Corp. III (FTACU),FTACU
                    NASDAQ Equity,FinTech Acquisition Corp. III (FTACW),FTACW
                    NASDAQ Equity,"FireEye, Inc. (FEYE)",FEYE
                    NASDAQ Equity,First Bancorp (FBNC),FBNC
                    NASDAQ Equity,"First Bancorp, Inc (ME) (FNLC)",FNLC
                    NASDAQ Equity,First Bank (FRBA),FRBA
                    NASDAQ Equity,First Busey Corporation (BUSE),BUSE
                    NASDAQ Equity,"First Business Financial Services, Inc. (FBIZ)",FBIZ
                    NASDAQ Equity,"First Capital, Inc. (FCAP)",FCAP
                    NASDAQ Equity,First Choice Bancorp (FCBP),FCBP
                    NASDAQ Equity,"First Citizens BancShares, Inc. (FCNCA)",FCNCA
                    NASDAQ Equity,"First Community Bankshares, Inc. (FCBC)",FCBC
                    NASDAQ Equity,First Community Corporation (FCCO),FCCO
                    NASDAQ Equity,First Defiance Financial Corp. (FDEF),FDEF
                    NASDAQ Equity,First Financial Bancorp. (FFBC),FFBC
                    NASDAQ Equity,"First Financial Bankshares, Inc. (FFIN)",FFIN
                    NASDAQ Equity,First Financial Corporation Indiana (THFF),THFF
                    NASDAQ Equity,"First Financial Northwest, Inc. (FFNW)",FFNW
                    NASDAQ Equity,First Foundation Inc. (FFWM),FFWM
                    NASDAQ Equity,"First Guaranty Bancshares, Inc. (FGBI)",FGBI
                    NASDAQ Equity,"First Hawaiian, Inc. (FHB)",FHB
                    NASDAQ Equity,First Internet Bancorp (INBK),INBK
                    NASDAQ Equity,First Internet Bancorp (INBKL),INBKL
                    NASDAQ Equity,First Internet Bancorp (INBKZ),INBKZ
                    NASDAQ Equity,"First Interstate BancSystem, Inc. (FIBK)",FIBK
                    NASDAQ Equity,First Merchants Corporation (FRME),FRME
                    NASDAQ Equity,"First Mid Bancshares, Inc. (FMBH)",FMBH
                    NASDAQ Equity,"First Midwest Bancorp, Inc. (FMBI)",FMBI
                    NASDAQ Equity,First National Corporation (FXNC),FXNC
                    NASDAQ Equity,First Northwest Bancorp (FNWB),FNWB
                    NASDAQ Equity,"First Savings Financial Group, Inc. (FSFG)",FSFG
                    NASDAQ Equity,"First Solar, Inc. (FSLR)",FSLR
                    NASDAQ Equity,First Trust Alternative Absolute Return Strategy ETF (FAAR),FAAR
                    NASDAQ Equity,First Trust Asia Pacific Ex-Japan AlphaDEX Fund (FPA),FPA
                    NASDAQ Equity,First Trust BICK Index Fund (BICK),BICK
                    NASDAQ Equity,First Trust Brazil AlphaDEX Fund (FBZ),FBZ
                    NASDAQ Equity,First Trust BuyWrite Income ETF (FTHI),FTHI
                    NASDAQ Equity,First Trust California Municipal High income ETF (FCAL),FCAL
                    NASDAQ Equity,First Trust Canada AlphaDEX Fund (FCAN),FCAN
                    NASDAQ Equity,First Trust Capital Strength ETF (FTCS),FTCS
                    NASDAQ Equity,First Trust CEF Income Opportunity ETF (FCEF),FCEF
                    NASDAQ Equity,First Trust China AlphaDEX Fund (FCA),FCA
                    NASDAQ Equity,First Trust Cloud Computing ETF (SKYY),SKYY
                    NASDAQ Equity,First Trust Developed International Equity Select ETF (RNDM),RNDM
                    NASDAQ Equity,First Trust Developed Markets Ex-US AlphaDEX Fund (FDT),FDT
                    NASDAQ Equity,First Trust Developed Markets ex-US Small Cap AlphaDEX Fund (FDTS),FDTS
                    NASDAQ Equity,First Trust Dorsey Wright Dynamic Focus 5 ETF (FVC),FVC
                    NASDAQ Equity,First Trust Dorsey Wright Focus 5 ETF (FV),FV
                    NASDAQ Equity,First Trust Dorsey Wright International Focus 5 ETF (IFV),IFV
                    NASDAQ Equity,First Trust Dorsey Wright Momentum & Dividend ETF (DDIV),DDIV
                    NASDAQ Equity,First Trust Dorsey Wright Momentum & Low Volatility ETF (DVOL),DVOL
                    NASDAQ Equity,First Trust Dorsey Wright Momentum & Value ETF (DVLU),DVLU
                    NASDAQ Equity,First Trust Dorsey Wright People&#39;s Portfolio ETF (DWPP),DWPP
                    NASDAQ Equity,First Trust DorseyWright DALI 1 ETF (DALI),DALI
                    NASDAQ Equity,First Trust Dow Jones International Internet ETF (FDNI),FDNI
                    NASDAQ Equity,First Trust Emerging Markets AlphaDEX Fund (FEM),FEM
                    NASDAQ Equity,First Trust Emerging Markets Equity Select ETF (RNEM),RNEM
                    NASDAQ Equity,First Trust Emerging Markets Local Currency Bond ETF (FEMB),FEMB
                    NASDAQ Equity,First Trust Emerging Markets Small Cap AlphaDEX Fund (FEMS),FEMS
                    NASDAQ Equity,First Trust Enhanced Short Maturity ETF (FTSM),FTSM
                    NASDAQ Equity,First Trust Europe AlphaDEX Fund (FEP),FEP
                    NASDAQ Equity,First Trust Eurozone AlphaDEX ETF (FEUZ),FEUZ
                    NASDAQ Equity,First Trust Germany AlphaDEX Fund (FGM),FGM
                    NASDAQ Equity,First Trust Global Tactical Commodity Strategy Fund (FTGC),FTGC
                    NASDAQ Equity,First Trust Hedged BuyWrite Income ETF (FTLB),FTLB
                    NASDAQ Equity,First Trust High Yield Long/Short ETF (HYLS),HYLS
                    NASDAQ Equity,First Trust Hong Kong AlphaDEX Fund (FHK),FHK
                    NASDAQ Equity,First Trust India Nifty 50 Equal Weight ETF (NFTY),NFTY
                    NASDAQ Equity,First Trust Indxx Global Agriculture ETF (FTAG),FTAG
                    NASDAQ Equity,First Trust Indxx Global Natural Resources Income ETF (FTRI),FTRI
                    NASDAQ Equity,First Trust Indxx Innovative Transaction & Process ETF (LEGR),LEGR
                    NASDAQ Equity,First Trust Indxx NextG ETF (NXTG),NXTG
                    NASDAQ Equity,First Trust International Equity Opportunities ETF (FPXI),FPXI
                    NASDAQ Equity,First Trust IPOX Europe Equity Opportunities ETF (FPXE),FPXE
                    NASDAQ Equity,First Trust Japan AlphaDEX Fund (FJP),FJP
                    NASDAQ Equity,First Trust Large Cap Core AlphaDEX Fund (FEX),FEX
                    NASDAQ Equity,First Trust Large Cap Growth AlphaDEX Fund (FTC),FTC
                    NASDAQ Equity,First Trust Large Cap US Equity Select ETF (RNLC),RNLC
                    NASDAQ Equity,First Trust Large Cap Value AlphaDEX Fund (FTA),FTA
                    NASDAQ Equity,First Trust Latin America AlphaDEX Fund (FLN),FLN
                    NASDAQ Equity,First Trust Low Duration Opportunities ETF (LMBS),LMBS
                    NASDAQ Equity,First Trust Low Duration Strategic Focus ETF (LDSF),LDSF
                    NASDAQ Equity,First Trust Managed Municipal ETF (FMB),FMB
                    NASDAQ Equity,First Trust Mega Cap AlphaDEX Fund (FMK),FMK
                    NASDAQ Equity,First Trust Mid Cap Core AlphaDEX Fund (FNX),FNX
                    NASDAQ Equity,First Trust Mid Cap Growth AlphaDEX Fund (FNY),FNY
                    NASDAQ Equity,First Trust Mid Cap US Equity Select ETF (RNMC),RNMC
                    NASDAQ Equity,First Trust Mid Cap Value AlphaDEX Fund (FNK),FNK
                    NASDAQ Equity,First Trust Multi Cap Growth AlphaDEX Fund (FAD),FAD
                    NASDAQ Equity,First Trust Multi Cap Value AlphaDEX Fund (FAB),FAB
                    NASDAQ Equity,First Trust Multi-Asset Diversified Income Index Fund (MDIV),MDIV
                    NASDAQ Equity,First Trust Municipal CEF Income Opportunity ETF (MCEF),MCEF
                    NASDAQ Equity,First Trust Municipal High Income ETF (FMHI),FMHI
                    NASDAQ Equity,First Trust NASDAQ ABA Community Bank Index Fund (QABA),QABA
                    NASDAQ Equity,First Trust Nasdaq Artificial Intelligence and Robotics ETF (ROBT),ROBT
                    NASDAQ Equity,First Trust Nasdaq Bank ETF (FTXO),FTXO
                    NASDAQ Equity,First Trust NASDAQ Clean Edge Green Energy Index Fund (QCLN),QCLN
                    NASDAQ Equity,First Trust NASDAQ Clean Edge Smart Grid Infrastructure Index  (GRID),GRID
                    NASDAQ Equity,First Trust NASDAQ Cybersecurity ETF (CIBR),CIBR
                    NASDAQ Equity,First Trust Nasdaq Food & Beverage ETF (FTXG),FTXG
                    NASDAQ Equity,First Trust NASDAQ Global Auto Index Fund (CARZ),CARZ
                    NASDAQ Equity,First Trust Nasdaq Oil & Gas ETF (FTXN),FTXN
                    NASDAQ Equity,First Trust Nasdaq Pharmaceuticals ETF (FTXH),FTXH
                    NASDAQ Equity,First Trust Nasdaq Retail ETF (FTXD),FTXD
                    NASDAQ Equity,First Trust Nasdaq Semiconductor ETF (FTXL),FTXL
                    NASDAQ Equity,First Trust NASDAQ Technology Dividend Index Fund (TDIV),TDIV
                    NASDAQ Equity,First Trust Nasdaq Transportation ETF (FTXR),FTXR
                    NASDAQ Equity,First Trust NASDAQ-100 Equal Weighted Index Fund (QQEW),QQEW
                    NASDAQ Equity,First Trust NASDAQ-100 Ex-Technology Sector Index Fund (QQXT),QQXT
                    NASDAQ Equity,First Trust NASDAQ-100- Technology Index Fund (QTEC),QTEC
                    NASDAQ Equity,First Trust RBA American Industrial Renaissance ETF (AIRR),AIRR
                    NASDAQ Equity,First Trust Rising Dividend Achievers ETF (RDVY),RDVY
                    NASDAQ Equity,First Trust RiverFront Dynamic Asia Pacific ETF (RFAP),RFAP
                    NASDAQ Equity,First Trust RiverFront Dynamic Developed International ETF (RFDI),RFDI
                    NASDAQ Equity,First Trust RiverFront Dynamic Emerging Markets ETF (RFEM),RFEM
                    NASDAQ Equity,First Trust RiverFront Dynamic Europe ETF (RFEU),RFEU
                    NASDAQ Equity,First Trust S&P International Dividend Aristocrats ETF (FID),FID
                    NASDAQ Equity,First Trust Senior Loan Fund ETF (FTSL),FTSL
                    NASDAQ Equity,First Trust Small Cap Core AlphaDEX Fund (FYX),FYX
                    NASDAQ Equity,First Trust Small Cap Growth AlphaDEX Fund (FYC),FYC
                    NASDAQ Equity,First Trust Small Cap US Equity Select ETF (RNSC),RNSC
                    NASDAQ Equity,First Trust Small Cap Value AlphaDEX Fund (FYT),FYT
                    NASDAQ Equity,First Trust SMID Cap Rising Dividend Achievers ETF (SDVY),SDVY
                    NASDAQ Equity,First Trust South Korea AlphaDEX Fund (FKO),FKO
                    NASDAQ Equity,First Trust SSI Strategic Convertible Securities ETF (FCVT),FCVT
                    NASDAQ Equity,First Trust Strategic Income ETF (FDIV),FDIV
                    NASDAQ Equity,First Trust Switzerland AlphaDEX Fund (FSZ),FSZ
                    NASDAQ Equity,First Trust TCW Opportunistic Fixed Income ETF (FIXD),FIXD
                    NASDAQ Equity,First Trust Total US Market AlphaDEX ETF (TUSA),TUSA
                    NASDAQ Equity,First Trust United Kingdom AlphaDEX Fund (FKU),FKU
                    NASDAQ Equity,First Trust US Equity Dividend Select ETF (RNDV),RNDV
                    NASDAQ Equity,First United Corporation (FUNC),FUNC
                    NASDAQ Equity,"First US Bancshares, Inc. (FUSB)",FUSB
                    NASDAQ Equity,"First Western Financial, Inc. (MYFW)",MYFW
                    NASDAQ Equity,"FirstCash, Inc. (FCFS)",FCFS
                    NASDAQ Equity,"Firsthand Technology Value Fund, Inc. (SVVC)",SVVC
                    NASDAQ Equity,FirstService Corporation (FSV),FSV
                    NASDAQ Equity,"Fiserv, Inc. (FISV)",FISV
                    NASDAQ Equity,"Five Below, Inc. (FIVE)",FIVE
                    NASDAQ Equity,"Five Prime Therapeutics, Inc. (FPRX)",FPRX
                    NASDAQ Equity,Five Star Senior Living Inc. (FVE),FVE
                    NASDAQ Equity,"Five9, Inc. (FIVN)",FIVN
                    NASDAQ Equity,Flex Ltd. (FLEX),FLEX
                    NASDAQ Equity,"Flex Pharma, Inc. (FLKS)",FLKS
                    NASDAQ Equity,"Flexion Therapeutics, Inc. (FLXN)",FLXN
                    NASDAQ Equity,FlexShares Credit-Scored US Corporate Bond Index Fund (SKOR),SKOR
                    NASDAQ Equity,FlexShares Credit-Scored US Long Corporate Bond Index Fund (LKOR),LKOR
                    NASDAQ Equity,FlexShares Disciplined Duration MBS Index Fund (MBSD),MBSD
                    NASDAQ Equity,FlexShares Real Assets Allocation Index Fund (ASET),ASET
                    NASDAQ Equity,FlexShares STOXX Global ESG Impact Index Fund (ESGG),ESGG
                    NASDAQ Equity,FlexShares STOXX US ESG Impact Index Fund (ESG),ESG
                    NASDAQ Equity,FlexShares US Quality Large Cap Index Fund (QLC),QLC
                    NASDAQ Equity,"FlexShopper, Inc. (FPAY)",FPAY
                    NASDAQ Equity,"FlexShopper, Inc. (FPAYW)",FPAYW
                    NASDAQ Equity,"Flexsteel Industries, Inc. (FLXS)",FLXS
                    NASDAQ Equity,"FLIR Systems, Inc. (FLIR)",FLIR
                    NASDAQ Equity,"Fluent, Inc. (FLNT)",FLNT
                    NASDAQ Equity,Fluidigm Corporation (FLDM),FLDM
                    NASDAQ Equity,Flushing Financial Corporation (FFIC),FFIC
                    NASDAQ Equity,FNCB Bancorp Inc. (FNCB),FNCB
                    NASDAQ Equity,Foamix Pharmaceuticals Ltd. (FOMX),FOMX
                    NASDAQ Equity,Focus Financial Partners Inc. (FOCS),FOCS
                    NASDAQ Equity,Fonar Corporation (FONR),FONR
                    NASDAQ Equity,"ForeScout Technologies, Inc. (FSCT)",FSCT
                    NASDAQ Equity,Foresight Autonomous Holdings Ltd. (FRSX),FRSX
                    NASDAQ Equity,"FormFactor, Inc. (FORM)",FORM
                    NASDAQ Equity,Formula Systems (1985) Ltd. (FORTY),FORTY
                    NASDAQ Equity,"Forrester Research, Inc. (FORR)",FORR
                    NASDAQ Equity,"Forterra, Inc. (FRTA)",FRTA
                    NASDAQ Equity,"Fortinet, Inc. (FTNT)",FTNT
                    NASDAQ Equity,"Fortress Biotech, Inc. (FBIO)",FBIO
                    NASDAQ Equity,"Fortress Biotech, Inc. (FBIOP)",FBIOP
                    NASDAQ Equity,"Forty Seven, Inc. (FTSV)",FTSV
                    NASDAQ Equity,Forum Merger II Corporation (FMCI),FMCI
                    NASDAQ Equity,Forum Merger II Corporation (FMCIU),FMCIU
                    NASDAQ Equity,Forum Merger II Corporation (FMCIW),FMCIW
                    NASDAQ Equity,Forward Air Corporation (FWRD),FWRD
                    NASDAQ Equity,"Forward Industries, Inc. (FORD)",FORD
                    NASDAQ Equity,Forward Pharma A/S (FWP),FWP
                    NASDAQ Equity,"Fossil Group, Inc. (FOSL)",FOSL
                    NASDAQ Equity,Fox Corporation (FOX),FOX
                    NASDAQ Equity,Fox Corporation (FOXA),FOXA
                    NASDAQ Equity,Fox Factory Holding Corp. (FOXF),FOXF
                    NASDAQ Equity,Francesca&#39;s Holdings Corporation (FRAN),FRAN
                    NASDAQ Equity,"Franklin Electric Co., Inc. (FELE)",FELE
                    NASDAQ Equity,Franklin Financial Services Corporation (FRAF),FRAF
                    NASDAQ Equity,"Fred&#39;s, Inc. (FRED)",FRED
                    NASDAQ Equity,"Freightcar America, Inc. (RAIL)",RAIL
                    NASDAQ Equity,"Frequency Electronics, Inc. (FEIM)",FEIM
                    NASDAQ Equity,"Freshpet, Inc. (FRPT)",FRPT
                    NASDAQ Equity,"frontdoor, inc. (FTDR)",FTDR
                    NASDAQ Equity,"FRONTEO, Inc. (FTEO)",FTEO
                    NASDAQ Equity,Frontier Communications Corporation (FTR),FTR
                    NASDAQ Equity,"FRP Holdings, Inc. (FRPH)",FRPH
                    NASDAQ Equity,"FS Bancorp, Inc. (FSBW)",FSBW
                    NASDAQ Equity,"FSB Bancorp, Inc. (FSBC)",FSBC
                    NASDAQ Equity,"Fuel Tech, Inc. (FTEK)",FTEK
                    NASDAQ Equity,"FuelCell Energy, Inc. (FCEL)",FCEL
                    NASDAQ Equity,"Fulgent Genetics, Inc. (FLGT)",FLGT
                    NASDAQ Equity,Fuling Global Inc. (FORK),FORK
                    NASDAQ Equity,"Full House Resorts, Inc. (FLL)",FLL
                    NASDAQ Equity,Fulton Financial Corporation (FULT),FULT
                    NASDAQ Equity,"Funko, Inc. (FNKO)",FNKO
                    NASDAQ Equity,Futu Holdings Limited (FHL),FHL
                    NASDAQ Equity,Future FinTech Group Inc. (FTFT),FTFT
                    NASDAQ Equity,"Fuwei Films (Holdings) Co., Ltd. (FFHL)",FFHL
                    NASDAQ Equity,"FVCBankcorp, Inc. (FVCB)",FVCB
                    NASDAQ Equity,"G. Willi-Food International,  Ltd. (WILC)",WILC
                    NASDAQ Equity,"G1 Therapeutics, Inc. (GTHX)",GTHX
                    NASDAQ Equity,"Gaia, Inc. (GAIA)",GAIA
                    NASDAQ Equity,Galapagos NV (GLPG),GLPG
                    NASDAQ Equity,Galectin Therapeutics Inc. (GALT),GALT
                    NASDAQ Equity,Galmed Pharmaceuticals Ltd. (GLMD),GLMD
                    NASDAQ Equity,Gamida Cell Ltd. (GMDA),GMDA
                    NASDAQ Equity,"Gaming and Leisure Properties, Inc. (GLPI)",GLPI
                    NASDAQ Equity,Garmin Ltd. (GRMN),GRMN
                    NASDAQ Equity,Garrison Capital Inc. (GARS),GARS
                    NASDAQ Equity,"GCI Liberty, Inc. (GLIBA)",GLIBA
                    NASDAQ Equity,"GCI Liberty, Inc. (GLIBP)",GLIBP
                    NASDAQ Equity,GDS Holdings Limited (GDS),GDS
                    NASDAQ Equity,Gemphire Therapeutics Inc. (GEMP),GEMP
                    NASDAQ Equity,Gencor Industries Inc. (GENC),GENC
                    NASDAQ Equity,General Finance Corporation (GFN),GFN
                    NASDAQ Equity,General Finance Corporation (GFNCP),GFNCP
                    NASDAQ Equity,General Finance Corporation (GFNSL),GFNSL
                    NASDAQ Equity,Genetic Technologies Ltd (GENE),GENE
                    NASDAQ Equity,GENFIT S.A. (GNFT),GNFT
                    NASDAQ Equity,"Genius Brands International, Inc. (GNUS)",GNUS
                    NASDAQ Equity,"GenMark Diagnostics, Inc. (GNMK)",GNMK
                    NASDAQ Equity,"Genocea Biosciences, Inc. (GNCA)",GNCA
                    NASDAQ Equity,"Genomic Health, Inc. (GHDX)",GHDX
                    NASDAQ Equity,"Genprex, Inc. (GNPX)",GNPX
                    NASDAQ Equity,Gentex Corporation (GNTX),GNTX
                    NASDAQ Equity,Gentherm Inc (THRM),THRM
                    NASDAQ Equity,Geospace Technologies Corporation (GEOS),GEOS
                    NASDAQ Equity,"German American Bancorp, Inc. (GABC)",GABC
                    NASDAQ Equity,Geron Corporation (GERN),GERN
                    NASDAQ Equity,"Gevo, Inc. (GEVO)",GEVO
                    NASDAQ Equity,"Gibraltar Industries, Inc. (ROCK)",ROCK
                    NASDAQ Equity,GigaMedia Limited (GIGM),GIGM
                    NASDAQ Equity,"G-III Apparel Group, LTD. (GIII)",GIII
                    NASDAQ Equity,Gilat Satellite Networks Ltd. (GILT),GILT
                    NASDAQ Equity,"Gilead Sciences, Inc. (GILD)",GILD
                    NASDAQ Equity,"Glacier Bancorp, Inc. (GBCI)",GBCI
                    NASDAQ Equity,Gladstone Capital Corporation (GLAD),GLAD
                    NASDAQ Equity,Gladstone Capital Corporation (GLADD),GLADD
                    NASDAQ Equity,Gladstone Capital Corporation (GLADN),GLADN
                    NASDAQ Equity,Gladstone Commercial Corporation (GOOD),GOOD
                    NASDAQ Equity,Gladstone Commercial Corporation (GOODM),GOODM
                    NASDAQ Equity,Gladstone Commercial Corporation (GOODO),GOODO
                    NASDAQ Equity,Gladstone Commercial Corporation (GOODP),GOODP
                    NASDAQ Equity,Gladstone Investment Corporation (GAIN),GAIN
                    NASDAQ Equity,Gladstone Investment Corporation (GAINL),GAINL
                    NASDAQ Equity,Gladstone Investment Corporation (GAINM),GAINM
                    NASDAQ Equity,Gladstone Land Corporation (LAND),LAND
                    NASDAQ Equity,Gladstone Land Corporation (LANDP),LANDP
                    NASDAQ Equity,Glen Burnie Bancorp (GLBZ),GLBZ
                    NASDAQ Equity,"Global Blood Therapeutics, Inc. (GBT)",GBT
                    NASDAQ Equity,Global Eagle Entertainment Inc. (ENT),ENT
                    NASDAQ Equity,Global Indemnity Limited (GBLI),GBLI
                    NASDAQ Equity,Global Indemnity Limited (GBLIL),GBLIL
                    NASDAQ Equity,Global Indemnity Limited (GBLIZ),GBLIZ
                    NASDAQ Equity,"Global Self Storage, Inc. (SELF)",SELF
                    NASDAQ Equity,"Global Water Resources, Inc. (GWRS)",GWRS
                    NASDAQ Equity,Global X Autonomous & Electric Vehicles ETF (DRIV),DRIV
                    NASDAQ Equity,Global X Cloud Computing ETF (CLOU),CLOU
                    NASDAQ Equity,Global X Conscious Companies ETF (KRMA),KRMA
                    NASDAQ Equity,Global X DAX Germany ETF (DAX),DAX
                    NASDAQ Equity,Global X E-commerce ETF (EBIZ),EBIZ
                    NASDAQ Equity,Global X FinTech ETF (FINX),FINX
                    NASDAQ Equity,Global X Funds Global X MSCI China Communication Services ETF (CHIC),CHIC
                    NASDAQ Equity,Global X Future Analytics Tech ETF (AIQ),AIQ
                    NASDAQ Equity,Global X Genomics & Biotechnology ETF (GNOM),GNOM
                    NASDAQ Equity,Global X Health & Wellness Thematic ETF (BFIT),BFIT
                    NASDAQ Equity,Global X Internet of Things ETF (SNSR),SNSR
                    NASDAQ Equity,Global X Longevity Thematic ETF (LNGR),LNGR
                    NASDAQ Equity,Global X Millennials Thematic ETF (MILN),MILN
                    NASDAQ Equity,Global X MSCI SuperDividend EAFE ETF (EFAS),EFAS
                    NASDAQ Equity,Global X NASDAQ-100 Covered Call ETF (QYLD),QYLD
                    NASDAQ Equity,Global X Robotics & Artificial Intelligence ETF (BOTZ),BOTZ
                    NASDAQ Equity,Global X S&P 500 Catholic Values ETF (CATH),CATH
                    NASDAQ Equity,Global X Social Media ETF (SOCL),SOCL
                    NASDAQ Equity,Global X SuperDividend Alternatives ETF (ALTY),ALTY
                    NASDAQ Equity,Global X SuperDividend REIT ETF (SRET),SRET
                    NASDAQ Equity,Global X YieldCo & Renewable Energy Income ETF (YLCO),YLCO
                    NASDAQ Equity,Globus Maritime Limited (GLBS),GLBS
                    NASDAQ Equity,Glu Mobile Inc. (GLUU),GLUU
                    NASDAQ Equity,"GlycoMimetics, Inc. (GLYC)",GLYC
                    NASDAQ Equity,Gogo Inc. (GOGO),GOGO
                    NASDAQ Equity,Golar LNG Limited (GLNG),GLNG
                    NASDAQ Equity,Golar LNG Partners LP (GMLP),GMLP
                    NASDAQ Equity,Golar LNG Partners LP (GMLPP),GMLPP
                    NASDAQ Equity,GOLDEN BULL LIMITED (DNJR),DNJR
                    NASDAQ Equity,"Golden Entertainment, Inc. (GDEN)",GDEN
                    NASDAQ Equity,Golden Ocean Group Limited (GOGL),GOGL
                    NASDAQ Equity,"Golub Capital BDC, Inc. (GBDC)",GBDC
                    NASDAQ Equity,Good Times Restaurants Inc. (GTIM),GTIM
                    NASDAQ Equity,"Goosehead Insurance, Inc. (GSHD)",GSHD
                    NASDAQ Equity,"GoPro, Inc. (GPRO)",GPRO
                    NASDAQ Equity,Gordon Pointe Acquisition Corp. (GPAQ),GPAQ
                    NASDAQ Equity,Gordon Pointe Acquisition Corp. (GPAQU),GPAQU
                    NASDAQ Equity,Gordon Pointe Acquisition Corp. (GPAQW),GPAQW
                    NASDAQ Equity,"Gores Holdings III, Inc. (GRSH)",GRSH
                    NASDAQ Equity,"Gores Holdings III, Inc. (GRSHU)",GRSHU
                    NASDAQ Equity,"Gores Holdings III, Inc. (GRSHW)",GRSHW
                    NASDAQ Equity,"Gores Metropoulos, Inc. (GMHI)",GMHI
                    NASDAQ Equity,"Gores Metropoulos, Inc. (GMHIU)",GMHIU
                    NASDAQ Equity,"Gores Metropoulos, Inc. (GMHIW)",GMHIW
                    NASDAQ Equity,"Gossamer Bio, Inc. (GOSS)",GOSS
                    NASDAQ Equity,"Grand Canyon Education, Inc. (LOPE)",LOPE
                    NASDAQ Equity,"GRAVITY Co., Ltd. (GRVY)",GRVY
                    NASDAQ Equity,Great Elm Capital Corp. (GECC),GECC
                    NASDAQ Equity,Great Elm Capital Corp. (GECCL),GECCL
                    NASDAQ Equity,Great Elm Capital Corp. (GECCM),GECCM
                    NASDAQ Equity,Great Elm Capital Corp. (GECCN),GECCN
                    NASDAQ Equity,"Great Elm Capital Group, Inc.  (GEC)",GEC
                    NASDAQ Equity,Great Lakes Dredge & Dock Corporation (GLDD),GLDD
                    NASDAQ Equity,"Great Southern Bancorp, Inc. (GSBC)",GSBC
                    NASDAQ Equity,"Green Brick Partners, Inc. (GRBK)",GRBK
                    NASDAQ Equity,Green Plains Partners LP (GPP),GPP
                    NASDAQ Equity,"Green Plains, Inc. (GPRE)",GPRE
                    NASDAQ Equity,"Greene County Bancorp, Inc. (GCBC)",GCBC
                    NASDAQ Equity,Greenland Acquisition Corporation (GLAC),GLAC
                    NASDAQ Equity,Greenland Acquisition Corporation (GLACR),GLACR
                    NASDAQ Equity,Greenland Acquisition Corporation (GLACU),GLACU
                    NASDAQ Equity,Greenland Acquisition Corporation (GLACW),GLACW
                    NASDAQ Equity,"Greenlane Holdings, Inc. (GNLN)",GNLN
                    NASDAQ Equity,"Greenlight Reinsurance, Ltd. (GLRE)",GLRE
                    NASDAQ Equity,Greenpro Capital Corp. (GRNQ),GRNQ
                    NASDAQ Equity,"GreenSky, Inc. (GSKY)",GSKY
                    NASDAQ Equity,Gridsum Holding Inc. (GSUM),GSUM
                    NASDAQ Equity,"Griffin Industrial Realty, Inc. (GRIF)",GRIF
                    NASDAQ Equity,"Grifols, S.A. (GRFS)",GRFS
                    NASDAQ Equity,Grindrod Shipping Holdings Ltd. (GRIN),GRIN
                    NASDAQ Equity,"Gritstone Oncology, Inc. (GRTS)",GRTS
                    NASDAQ Equity,Grocery Outlet Holding Corp. (GO),GO
                    NASDAQ Equity,"Groupon, Inc. (GRPN)",GRPN
                    NASDAQ Equity,Grupo Aeroportuario del Centro Norte S.A.B. de C.V. (OMAB),OMAB
                    NASDAQ Equity,Grupo Financiero Galicia S.A. (GGAL),GGAL
                    NASDAQ Equity,"GSE Systems, Inc. (GVP)",GVP
                    NASDAQ Equity,"GSI Technology, Inc. (GSIT)",GSIT
                    NASDAQ Equity,GSV Capital Corp (GSVC),GSVC
                    NASDAQ Equity,"GTY Technology Holdings, Inc. (GTYH)",GTYH
                    NASDAQ Equity,"Guaranty Bancshares, Inc. (GNTY)",GNTY
                    NASDAQ Equity,"Guaranty Federal Bancshares, Inc. (GFED)",GFED
                    NASDAQ Equity,"Guardant Health, Inc. (GH)",GH
                    NASDAQ Equity,"Guardion Health Sciences, Inc. (GHSI)",GHSI
                    NASDAQ Equity,"Gulf Island Fabrication, Inc. (GIFI)",GIFI
                    NASDAQ Equity,"Gulf Resources, Inc. (GURE)",GURE
                    NASDAQ Equity,Gulfport Energy Corporation (GPOR),GPOR
                    NASDAQ Equity,GW Pharmaceuticals Plc (GWPH),GWPH
                    NASDAQ Equity,"GWG Holdings, Inc (GWGH)",GWGH
                    NASDAQ Equity,GX Acquisiton Corp. (GXGXU),GXGXU
                    NASDAQ Equity,"Gyrodyne , LLC (GYRO)",GYRO
                    NASDAQ Equity,"H&E Equipment Services, Inc. (HEES)",HEES
                    NASDAQ Equity,Hailiang Education Group Inc. (HLG),HLG
                    NASDAQ Equity,Hallador Energy Company (HNRG),HNRG
                    NASDAQ Equity,"Hallmark Financial Services, Inc. (HALL)",HALL
                    NASDAQ Equity,"Halozyme Therapeutics, Inc. (HALO)",HALO
                    NASDAQ Equity,Hamilton Lane Incorporated (HLNE),HLNE
                    NASDAQ Equity,"Hancock Jaffe Laboratories, Inc. (HJLI)",HJLI
                    NASDAQ Equity,"Hancock Jaffe Laboratories, Inc. (HJLIW)",HJLIW
                    NASDAQ Equity,Hancock Whitney Corporation (HWC),HWC
                    NASDAQ Equity,Hancock Whitney Corporation (HWCPL),HWCPL
                    NASDAQ Equity,Hanmi Financial Corporation (HAFC),HAFC
                    NASDAQ Equity,"HarborOne Bancorp, Inc. (HONE)",HONE
                    NASDAQ Equity,Harmonic Inc. (HLIT),HLIT
                    NASDAQ Equity,"Harpoon Therapeutics, Inc. (HARP)",HARP
                    NASDAQ Equity,"Harrow Health, Inc. (HROW)",HROW
                    NASDAQ Equity,"Harvard Bioscience, Inc. (HBIO)",HBIO
                    NASDAQ Equity,Harvest Capital Credit Corporation (HCAP),HCAP
                    NASDAQ Equity,Harvest Capital Credit Corporation (HCAPZ),HCAPZ
                    NASDAQ Equity,"Hasbro, Inc. (HAS)",HAS
                    NASDAQ Equity,"Hawaiian Holdings, Inc. (HA)",HA
                    NASDAQ Equity,"Hawkins, Inc. (HWKN)",HWKN
                    NASDAQ Equity,"Hawthorn Bancshares, Inc. (HWBK)",HWBK
                    NASDAQ Equity,Haymaker Acquisition Corp. II (HYACU),HYACU
                    NASDAQ Equity,"Haynes International, Inc. (HAYN)",HAYN
                    NASDAQ Equity,"HD Supply Holdings, Inc. (HDS)",HDS
                    NASDAQ Equity,HeadHunter Group PLC (HHR),HHR
                    NASDAQ Equity,"Health Insurance Innovations, Inc. (HIIQ)",HIIQ
                    NASDAQ Equity,Health Sciences Acquisitions Corporation (HSAC),HSAC
                    NASDAQ Equity,Health Sciences Acquisitions Corporation (HSACU),HSACU
                    NASDAQ Equity,Health Sciences Acquisitions Corporation (HSACW),HSACW
                    NASDAQ Equity,"Healthcare Services Group, Inc. (HCSG)",HCSG
                    NASDAQ Equity,"HealthEquity, Inc. (HQY)",HQY
                    NASDAQ Equity,"HealthStream, Inc. (HSTM)",HSTM
                    NASDAQ Equity,"Heartland Express, Inc. (HTLD)",HTLD
                    NASDAQ Equity,"Heartland Financial USA, Inc. (HTLF)",HTLF
                    NASDAQ Equity,"Heat Biologics, Inc. (HTBX)",HTBX
                    NASDAQ Equity,"Hebron Technology Co., Ltd. (HEBT)",HEBT
                    NASDAQ Equity,"Heidrick & Struggles International, Inc. (HSII)",HSII
                    NASDAQ Equity,Helen of Troy Limited (HELE),HELE
                    NASDAQ Equity,"Helios Technologies, Inc. (HLIO)",HLIO
                    NASDAQ Equity,"Helius Medical Technologies, Inc. (HSDT)",HSDT
                    NASDAQ Equity,"Hemisphere Media Group, Inc. (HMTV)",HMTV
                    NASDAQ Equity,"Hennessy Advisors, Inc. (HNNA)",HNNA
                    NASDAQ Equity,Hennessy Capital Acquisition Corp. IV (HCAC),HCAC
                    NASDAQ Equity,Hennessy Capital Acquisition Corp. IV (HCACU),HCACU
                    NASDAQ Equity,Hennessy Capital Acquisition Corp. IV (HCACW),HCACW
                    NASDAQ Equity,"Henry Schein, Inc. (HSIC)",HSIC
                    NASDAQ Equity,Heritage Commerce Corp (HTBK),HTBK
                    NASDAQ Equity,Heritage Financial Corporation (HFWA),HFWA
                    NASDAQ Equity,"Heritage-Crystal Clean, Inc. (HCCI)",HCCI
                    NASDAQ Equity,"Herman Miller, Inc. (MLHR)",MLHR
                    NASDAQ Equity,"Heron Therapeutics, Inc.   (HRTX)",HRTX
                    NASDAQ Equity,Heska Corporation (HSKA),HSKA
                    NASDAQ Equity,Hexindai Inc. (HX),HX
                    NASDAQ Equity,HF Foods Group Inc. (HFFG),HFFG
                    NASDAQ Equity,"Hibbett Sports, Inc. (HIBB)",HIBB
                    NASDAQ Equity,Highland/iBoxx Senior Loan ETF (SNLN),SNLN
                    NASDAQ Equity,Highpower International Inc (HPJ),HPJ
                    NASDAQ Equity,Highway Holdings Limited (HIHO),HIHO
                    NASDAQ Equity,"Himax Technologies, Inc. (HIMX)",HIMX
                    NASDAQ Equity,Hingham Institution for Savings (HIFS),HIFS
                    NASDAQ Equity,Histogenics Corporation (HSGX),HSGX
                    NASDAQ Equity,HL Acquisitions Corp. (HCCH),HCCH
                    NASDAQ Equity,HL Acquisitions Corp. (HCCHR),HCCHR
                    NASDAQ Equity,HL Acquisitions Corp. (HCCHU),HCCHU
                    NASDAQ Equity,HL Acquisitions Corp. (HCCHW),HCCHW
                    NASDAQ Equity,"HMN Financial, Inc. (HMNF)",HMNF
                    NASDAQ Equity,HMS Holdings Corp (HMSY),HMSY
                    NASDAQ Equity,"Hollysys Automation Technologies, Ltd. (HOLI)",HOLI
                    NASDAQ Equity,"Hologic, Inc. (HOLX)",HOLX
                    NASDAQ Equity,"Home Bancorp, Inc. (HBCP)",HBCP
                    NASDAQ Equity,"Home BancShares, Inc. (HOMB)",HOMB
                    NASDAQ Equity,"Home Federal Bancorp, Inc. of Louisiana (HFBL)",HFBL
                    NASDAQ Equity,"HomeStreet, Inc. (HMST)",HMST
                    NASDAQ Equity,"HomeTrust Bancshares, Inc. (HTBI)",HTBI
                    NASDAQ Equity,"Homology Medicines, Inc. (FIXX)",FIXX
                    NASDAQ Equity,Hooker Furniture Corporation (HOFT),HOFT
                    NASDAQ Equity,HOOKIPA Pharma Inc. (HOOK),HOOK
                    NASDAQ Equity,"Hope Bancorp, Inc. (HOPE)",HOPE
                    NASDAQ Equity,"HopFed Bancorp, Inc. (HFBC)",HFBC
                    NASDAQ Equity,"Horizon Bancorp, Inc. (HBNC)",HBNC
                    NASDAQ Equity,Horizon Technology Finance Corporation (HRZN),HRZN
                    NASDAQ Equity,Horizon Therapeutics Public Limited Company (HZNP),HZNP
                    NASDAQ Equity,Hospitality Properties Trust (HPT),HPT
                    NASDAQ Equity,"Hostess Brands, Inc. (TWNK)",TWNK
                    NASDAQ Equity,"Hostess Brands, Inc. (TWNKW)",TWNKW
                    NASDAQ Equity,"Hoth Therapeutics, Inc. (HOTH)",HOTH
                    NASDAQ Equity,Houghton Mifflin Harcourt Company (HMHC),HMHC
                    NASDAQ Equity,Houston Wire & Cable Company (HWCC),HWCC
                    NASDAQ Equity,Hovnanian Enterprises Inc (HOVNP),HOVNP
                    NASDAQ Equity,"Howard Bancorp, Inc. (HBMD)",HBMD
                    NASDAQ Equity,"HTG Molecular Diagnostics, Inc. (HTGM)",HTGM
                    NASDAQ Equity,Huazhu Group Limited (HTHT),HTHT
                    NASDAQ Equity,"Hub Group, Inc. (HUBG)",HUBG
                    NASDAQ Equity,"Hudson Global, Inc. (HSON)",HSON
                    NASDAQ Equity,"Hudson Technologies, Inc. (HDSN)",HDSN
                    NASDAQ Equity,Huntington Bancshares Incorporated (HBAN),HBAN
                    NASDAQ Equity,Huntington Bancshares Incorporated (HBANN),HBANN
                    NASDAQ Equity,Huntington Bancshares Incorporated (HBANO),HBANO
                    NASDAQ Equity,"Hurco Companies, Inc. (HURC)",HURC
                    NASDAQ Equity,Huron Consulting Group Inc. (HURN),HURN
                    NASDAQ Equity,Hutchison China MediTech Limited (HCM),HCM
                    NASDAQ Equity,"Huttig Building Products, Inc. (HBP)",HBP
                    NASDAQ Equity,"HV Bancorp, Inc. (HVBC)",HVBC
                    NASDAQ Equity,Hydrogenics Corporation (HYGS),HYGS
                    NASDAQ Equity,HyreCar Inc. (HYRE),HYRE
                    NASDAQ Equity,"I.D. Systems, Inc. (IDSY)",IDSY
                    NASDAQ Equity,"i3 Verticals, Inc. (IIIV)",IIIV
                    NASDAQ Equity,IAC/InterActiveCorp (IAC),IAC
                    NASDAQ Equity,IBERIABANK Corporation (IBKC),IBKC
                    NASDAQ Equity,IBERIABANK Corporation (IBKCN),IBKCN
                    NASDAQ Equity,IBERIABANK Corporation (IBKCO),IBKCO
                    NASDAQ Equity,IBERIABANK Corporation (IBKCP),IBKCP
                    NASDAQ Equity,icad inc. (ICAD),ICAD
                    NASDAQ Equity,Icahn Enterprises L.P. (IEP),IEP
                    NASDAQ Equity,"ICC Holdings, Inc. (ICCH)",ICCH
                    NASDAQ Equity,"ICF International, Inc. (ICFI)",ICFI
                    NASDAQ Equity,Ichor Holdings (ICHR),ICHR
                    NASDAQ Equity,iClick Interactive Asia Group Limited (ICLK),ICLK
                    NASDAQ Equity,ICON plc (ICLR),ICLR
                    NASDAQ Equity,"Iconix Brand Group, Inc. (ICON)",ICON
                    NASDAQ Equity,"ICU Medical, Inc. (ICUI)",ICUI
                    NASDAQ Equity,Ideal Power Inc. (IPWR),IPWR
                    NASDAQ Equity,"Ideanomics, Inc. (IDEX)",IDEX
                    NASDAQ Equity,"IDEAYA Biosciences, Inc. (IDYA)",IDYA
                    NASDAQ Equity,"Identiv, Inc. (INVE)",INVE
                    NASDAQ Equity,"Idera Pharmaceuticals, Inc. (IDRA)",IDRA
                    NASDAQ Equity,"IDEXX Laboratories, Inc. (IDXX)",IDXX
                    NASDAQ Equity,"IES Holdings, Inc. (IESC)",IESC
                    NASDAQ Equity,"IF Bancorp, Inc. (IROQ)",IROQ
                    NASDAQ Equity,iFresh Inc. (IFMK),IFMK
                    NASDAQ Equity,IHS Markit Ltd. (INFO),INFO
                    NASDAQ Equity,II-VI Incorporated (IIVI),IIVI
                    NASDAQ Equity,Ikonics Corporation (IKNX),IKNX
                    NASDAQ Equity,"Illumina, Inc. (ILMN)",ILMN
                    NASDAQ Equity,"IMAC Holdings, Inc. (IMAC)",IMAC
                    NASDAQ Equity,"IMAC Holdings, Inc. (IMACW)",IMACW
                    NASDAQ Equity,"Image Sensing Systems, Inc. (ISNS)",ISNS
                    NASDAQ Equity,Immersion Corporation (IMMR),IMMR
                    NASDAQ Equity,ImmuCell Corporation (ICCC),ICCC
                    NASDAQ Equity,"Immunic, Inc.  (IMUX)",IMUX
                    NASDAQ Equity,"ImmunoGen, Inc. (IMGN)",IMGN
                    NASDAQ Equity,"Immunomedics, Inc. (IMMU)",IMMU
                    NASDAQ Equity,Immuron Limited (IMRN),IMRN
                    NASDAQ Equity,Immuron Limited (IMRNW),IMRNW
                    NASDAQ Equity,Immutep Limited (IMMP),IMMP
                    NASDAQ Equity,"Impinj, Inc. (PI)",PI
                    NASDAQ Equity,IMV Inc. (IMV),IMV
                    NASDAQ Equity,Incyte Corporation (INCY),INCY
                    NASDAQ Equity,Independent Bank Corp. (INDB),INDB
                    NASDAQ Equity,Independent Bank Corporation (IBCP),IBCP
                    NASDAQ Equity,"Independent Bank Group, Inc (IBTX)",IBTX
                    NASDAQ Equity,Industrial Logistics Properties Trust (ILPT),ILPT
                    NASDAQ Equity,"Industrial Services of America, Inc. (IDSA)",IDSA
                    NASDAQ Equity,Infinera Corporation (INFN),INFN
                    NASDAQ Equity,"Infinity Pharmaceuticals, Inc. (INFI)",INFI
                    NASDAQ Equity,InflaRx N.V. (IFRX),IFRX
                    NASDAQ Equity,"Information Services Group, Inc. (III)",III
                    NASDAQ Equity,"Infrastructure and Energy Alternatives, Inc. (IEA)",IEA
                    NASDAQ Equity,"Infrastructure and Energy Alternatives, Inc. (IEAWW)",IEAWW
                    NASDAQ Equity,"Ingles Markets, Incorporated (IMKTA)",IMKTA
                    NASDAQ Equity,INmune Bio Inc. (INMB),INMB
                    NASDAQ Equity,"InnerWorkings, Inc. (INWK)",INWK
                    NASDAQ Equity,Innodata Inc. (INOD),INOD
                    NASDAQ Equity,"Innophos Holdings, Inc. (IPHS)",IPHS
                    NASDAQ Equity,Innospec Inc. (IOSP),IOSP
                    NASDAQ Equity,"Innovate Biopharmaceuticals, Inc. (INNT)",INNT
                    NASDAQ Equity,"Innovative Solutions and Support, Inc. (ISSC)",ISSC
                    NASDAQ Equity,"Innoviva, Inc. (INVA)",INVA
                    NASDAQ Equity,"Inogen, Inc (INGN)",INGN
                    NASDAQ Equity,"Inovalon Holdings, Inc. (INOV)",INOV
                    NASDAQ Equity,"Inovio Pharmaceuticals, Inc. (INO)",INO
                    NASDAQ Equity,Inpixon  (INPX),INPX
                    NASDAQ Equity,Inseego Corp. (INSG),INSG
                    NASDAQ Equity,"Insight Enterprises, Inc. (NSIT)",NSIT
                    NASDAQ Equity,"Insignia Systems, Inc. (ISIG)",ISIG
                    NASDAQ Equity,"Insmed, Inc. (INSM)",INSM
                    NASDAQ Equity,"Inspired Entertainment, Inc. (INSE)",INSE
                    NASDAQ Equity,"Insteel Industries, Inc. (IIIN)",IIIN
                    NASDAQ Equity,Insulet Corporation (PODD),PODD
                    NASDAQ Equity,Insurance Acquisition Corp. (INSU),INSU
                    NASDAQ Equity,Insurance Acquisition Corp. (INSUU),INSUU
                    NASDAQ Equity,Insurance Acquisition Corp. (INSUW),INSUW
                    NASDAQ Equity,Intec Pharma Ltd. (NTEC),NTEC
                    NASDAQ Equity,Integra LifeSciences Holdings Corporation (IART),IART
                    NASDAQ Equity,Integrated Media Technology Limited (IMTE),IMTE
                    NASDAQ Equity,Intel Corporation (INTC),INTC
                    NASDAQ Equity,"Intellia Therapeutics, Inc. (NTLA)",NTLA
                    NASDAQ Equity,"Inter Parfums, Inc. (IPAR)",IPAR
                    NASDAQ Equity,"Intercept Pharmaceuticals, Inc. (ICPT)",ICPT
                    NASDAQ Equity,"InterDigital, Inc. (IDCC)",IDCC
                    NASDAQ Equity,"Interface, Inc. (TILE)",TILE
                    NASDAQ Equity,"Intermolecular, Inc. (IMI)",IMI
                    NASDAQ Equity,Internap Corporation (INAP),INAP
                    NASDAQ Equity,International Bancshares Corporation (IBOC),IBOC
                    NASDAQ Equity,"International Money Express, Inc. (IMXI)",IMXI
                    NASDAQ Equity,International Speedway Corporation (ISCA),ISCA
                    NASDAQ Equity,Internet Gold Golden Lines Ltd. (IGLD),IGLD
                    NASDAQ Equity,"Interpace Diagnostics Group, Inc. (IDXG)",IDXG
                    NASDAQ Equity,"Intersect ENT, Inc. (XENT)",XENT
                    NASDAQ Equity,Interstate Power and Light Company (IPLDP),IPLDP
                    NASDAQ Equity,"Intevac, Inc. (IVAC)",IVAC
                    NASDAQ Equity,INTL FCStone Inc. (INTL),INTL
                    NASDAQ Equity,Intra-Cellular Therapies Inc. (ITCI),ITCI
                    NASDAQ Equity,Intrexon Corporation (XON),XON
                    NASDAQ Equity,IntriCon Corporation (IIN),IIN
                    NASDAQ Equity,Intuit Inc. (INTU),INTU
                    NASDAQ Equity,"Intuitive Surgical, Inc. (ISRG)",ISRG
                    NASDAQ Equity,Invesco 1-30 Laddered Treasury ETF (PLW),PLW
                    NASDAQ Equity,Invesco BLDRS Asia 50 ADR Index Fund (ADRA),ADRA
                    NASDAQ Equity,Invesco BLDRS Developed Markets 100 ADR Index Fund (ADRD),ADRD
                    NASDAQ Equity,Invesco BLDRS Emerging Markets 50 ADR Index Fund (ADRE),ADRE
                    NASDAQ Equity,Invesco BLDRS Europe Select ADR Index Fund (ADRU),ADRU
                    NASDAQ Equity,Invesco BuyBack Achievers ETF (PKW),PKW
                    NASDAQ Equity,Invesco Dividend Achievers ETF (PFM),PFM
                    NASDAQ Equity,Invesco DWA Basic Materials Momentum ETF (PYZ),PYZ
                    NASDAQ Equity,Invesco DWA Consumer Cyclicals Momentum ETF (PEZ),PEZ
                    NASDAQ Equity,Invesco DWA Consumer Staples Momentum ETF (PSL),PSL
                    NASDAQ Equity,Invesco DWA Developed Markets Momentum ETF (PIZ),PIZ
                    NASDAQ Equity,Invesco DWA Emerging Markets Momentum ETF (PIE),PIE
                    NASDAQ Equity,Invesco DWA Energy Momentum ETF (PXI),PXI
                    NASDAQ Equity,Invesco DWA Financial Momentum ETF (PFI),PFI
                    NASDAQ Equity,Invesco DWA Healthcare Momentum ETF (PTH),PTH
                    NASDAQ Equity,Invesco DWA Industrials Momentum ETF (PRN),PRN
                    NASDAQ Equity,Invesco DWA Momentum ETF (PDP),PDP
                    NASDAQ Equity,Invesco DWA NASDAQ Momentum ETF (DWAQ),DWAQ
                    NASDAQ Equity,Invesco DWA SmallCap Momentum ETF (DWAS),DWAS
                    NASDAQ Equity,Invesco DWA Tactical Multi-Asset Income ETF (DWIN),DWIN
                    NASDAQ Equity,Invesco DWA Tactical Sector Rotation ETF (DWTR),DWTR
                    NASDAQ Equity,Invesco DWA Technology Momentum ETF (PTF),PTF
                    NASDAQ Equity,Invesco DWA Utilities Momentum ETF (PUI),PUI
                    NASDAQ Equity,Invesco FTSE International Low Beta Equal Weight ETF (IDLB),IDLB
                    NASDAQ Equity,Invesco FTSE RAFI US 1500 Small-Mid ETF (PRFZ),PRFZ
                    NASDAQ Equity,Invesco Global Water ETF (PIO),PIO
                    NASDAQ Equity,Invesco Golden Dragon China ETF (PGJ),PGJ
                    NASDAQ Equity,Invesco High Yield Equity Dividend Achievers ETF (PEY),PEY
                    NASDAQ Equity,Invesco International BuyBack Achievers ETF (IPKW),IPKW
                    NASDAQ Equity,Invesco International Dividend Achievers ETF (PID),PID
                    NASDAQ Equity,Invesco KBW Bank ETF (KBWB),KBWB
                    NASDAQ Equity,Invesco KBW High Dividend Yield Financial ETF (KBWD),KBWD
                    NASDAQ Equity,Invesco KBW Premium Yield Equity REIT ETF (KBWY),KBWY
                    NASDAQ Equity,Invesco KBW Property & Casualty Insurance ETF (KBWP),KBWP
                    NASDAQ Equity,Invesco KBW Regional Banking ETF (KBWR),KBWR
                    NASDAQ Equity,Invesco LadderRite 0-5 Year Corporate Bond ETF (LDRI),LDRI
                    NASDAQ Equity,Invesco Nasdaq Internet ETF (PNQI),PNQI
                    NASDAQ Equity,Invesco Optimum Yield Diversified Commodity Strategy No K-1 ET (PDBC),PDBC
                    NASDAQ Equity,"Invesco QQQ Trust, Series 1 (QQQ)",QQQ
                    NASDAQ Equity,Invesco RAFI Strategic Developed ex-US ETF (ISDX),ISDX
                    NASDAQ Equity,Invesco RAFI Strategic Developed ex-US Small Company ETF (ISDS),ISDS
                    NASDAQ Equity,Invesco RAFI Strategic Emerging Markets ETF (ISEM),ISEM
                    NASDAQ Equity,Invesco RAFI Strategic US ETF (IUS),IUS
                    NASDAQ Equity,Invesco RAFI Strategic US Small Company ETF (IUSS),IUSS
                    NASDAQ Equity,Invesco Russell 1000 Low Beta Equal Weight ETF (USLB),USLB
                    NASDAQ Equity,Invesco S&P SmallCap Consumer Discretionary ETF (PSCD),PSCD
                    NASDAQ Equity,Invesco S&P SmallCap Consumer Staples ETF (PSCC),PSCC
                    NASDAQ Equity,Invesco S&P SmallCap Energy ETF (PSCE),PSCE
                    NASDAQ Equity,Invesco S&P SmallCap Financials ETF (PSCF),PSCF
                    NASDAQ Equity,Invesco S&P SmallCap Health Care ETF (PSCH),PSCH
                    NASDAQ Equity,Invesco S&P SmallCap Industrials ETF (PSCI),PSCI
                    NASDAQ Equity,Invesco S&P SmallCap Information Technology ETF (PSCT),PSCT
                    NASDAQ Equity,Invesco S&P SmallCap Materials ETF (PSCM),PSCM
                    NASDAQ Equity,Invesco S&P SmallCap Utilities & Communication Services ETF (PSCU),PSCU
                    NASDAQ Equity,Invesco Variable Rate Investment Grade ETF (VRIG),VRIG
                    NASDAQ Equity,Invesco Water Resources ETF (PHO),PHO
                    NASDAQ Equity,Investar Holding Corporation (ISTR),ISTR
                    NASDAQ Equity,"Investors Bancorp, Inc. (ISBC)",ISBC
                    NASDAQ Equity,Investors Title Company (ITIC),ITIC
                    NASDAQ Equity,InVivo Therapeutics Holdings Corp. (NVIV),NVIV
                    NASDAQ Equity,"Ionis Pharmaceuticals, Inc. (IONS)",IONS
                    NASDAQ Equity,"Iovance Biotherapeutics, Inc. (IOVA)",IOVA
                    NASDAQ Equity,IPG Photonics Corporation (IPGP),IPGP
                    NASDAQ Equity,iPic Entertainment Inc. (IPIC),IPIC
                    NASDAQ Equity,IQ Chaikin U.S. Large Cap ETF (CLRG),CLRG
                    NASDAQ Equity,IQ Chaikin U.S. Small Cap ETF (CSML),CSML
                    NASDAQ Equity,"iQIYI, Inc. (IQ)",IQ
                    NASDAQ Equity,iRadimed Corporation (IRMD),IRMD
                    NASDAQ Equity,"iRhythm Technologies, Inc. (IRTC)",IRTC
                    NASDAQ Equity,IRIDEX Corporation (IRIX),IRIX
                    NASDAQ Equity,Iridium Communications Inc (IRDM),IRDM
                    NASDAQ Equity,iRobot Corporation (IRBT),IRBT
                    NASDAQ Equity,"Ironwood Pharmaceuticals, Inc. (IRWD)",IRWD
                    NASDAQ Equity,IRSA Propiedades Comerciales S.A. (IRCP),IRCP
                    NASDAQ Equity,iShares 0-5 Year Investment Grade Corporate Bond ETF (SLQD),SLQD
                    NASDAQ Equity,iShares 1-3 Year International Treasury Bond ETF (ISHG),ISHG
                    NASDAQ Equity,iShares 1-3 Year Treasury Bond ETF (SHY),SHY
                    NASDAQ Equity,iShares 20+ Year Treasury Bond ETF (TLT),TLT
                    NASDAQ Equity,iShares 3-7 Year Treasury Bond ETF (IEI),IEI
                    NASDAQ Equity,iShares 7-10 Year Treasury Bond ETF (IEF),IEF
                    NASDAQ Equity,iShares Asia 50 ETF (AIA),AIA
                    NASDAQ Equity,iShares Broad USD Investment Grade Corporate Bond ETF (USIG),USIG
                    NASDAQ Equity,iShares Commodities Select Strategy ETF (COMT),COMT
                    NASDAQ Equity,iShares Core 1-5 Year USD Bond ETF (ISTB),ISTB
                    NASDAQ Equity,iShares Core MSCI Total International Stock ETF (IXUS),IXUS
                    NASDAQ Equity,iShares Core S&P U.S. Growth ETF (IUSG),IUSG
                    NASDAQ Equity,iShares Core S&P U.S. Value ETF (IUSV),IUSV
                    NASDAQ Equity,iShares Core Total USD Bond Market ETF (IUSB),IUSB
                    NASDAQ Equity,iShares Currency Hedged MSCI Germany ETF (HEWG),HEWG
                    NASDAQ Equity,iShares ESG 1-5 Year USD Corporate Bond ETF (SUSB),SUSB
                    NASDAQ Equity,iShares ESG MSCI EAFE ETF (ESGD),ESGD
                    NASDAQ Equity,iShares ESG MSCI EM ETF (ESGE),ESGE
                    NASDAQ Equity,iShares ESG MSCI USA ETF (ESGU),ESGU
                    NASDAQ Equity,iShares ESG MSCI USA Leaders ETF (SUSL),SUSL
                    NASDAQ Equity,iShares ESG USD Corporate Bond ETF (SUSC),SUSC
                    NASDAQ Equity,iShares Exponential Technologies ETF (XT),XT
                    NASDAQ Equity,iShares Fallen Angels USD Bond ETF (FALN),FALN
                    NASDAQ Equity,iShares FTSE EPRA/NAREIT Europe Index Fund (IFEU),IFEU
                    NASDAQ Equity,iShares FTSE EPRA/NAREIT Global Real Estate ex-U.S. Index Fund (IFGL),IFGL
                    NASDAQ Equity,iShares Global Green Bond ETF (BGRN),BGRN
                    NASDAQ Equity,iShares Global Infrastructure ETF (IGF),IGF
                    NASDAQ Equity,iShares GNMA Bond ETF (GNMA),GNMA
                    NASDAQ Equity,iShares iBoxx $ High Yield ex Oil & Gas Corporate Bond ETF (HYXE),HYXE
                    NASDAQ Equity,iShares Intermediate-Term Corporate Bond ETF (IGIB),IGIB
                    NASDAQ Equity,iShares International Treasury Bond ETF (IGOV),IGOV
                    NASDAQ Equity,iShares J.P. Morgan USD Emerging Markets Bond ETF (EMB),EMB
                    NASDAQ Equity,iShares MBS ETF (MBB),MBB
                    NASDAQ Equity,iShares Morningstar Mid-Cap ETF (JKI),JKI
                    NASDAQ Equity,iShares MSCI ACWI ex US Index Fund (ACWX),ACWX
                    NASDAQ Equity,iShares MSCI ACWI Index Fund (ACWI),ACWI
                    NASDAQ Equity,iShares MSCI All Country Asia ex Japan Index Fund (AAXJ),AAXJ
                    NASDAQ Equity,iShares MSCI Brazil Small-Cap ETF (EWZS),EWZS
                    NASDAQ Equity,iShares MSCI China ETF (MCHI),MCHI
                    NASDAQ Equity,iShares MSCI EAFE Small-Cap ETF (SCZ),SCZ
                    NASDAQ Equity,iShares MSCI Emerging Markets Asia ETF (EEMA),EEMA
                    NASDAQ Equity,iShares MSCI Emerging Markets ex China ETF (EMXC),EMXC
                    NASDAQ Equity,iShares MSCI Europe Financials Sector Index Fund (EUFN),EUFN
                    NASDAQ Equity,iShares MSCI Europe Small-Cap ETF (IEUS),IEUS
                    NASDAQ Equity,iShares MSCI Global Gold Miners ETF (RING),RING
                    NASDAQ Equity,iShares MSCI Global Impact ETF (SDG),SDG
                    NASDAQ Equity,iShares MSCI Japan Equal Weighted ETF (EWJE),EWJE
                    NASDAQ Equity,iShares MSCI Japan Value ETF (EWJV),EWJV
                    NASDAQ Equity,iShares MSCI New Zealand ETF (ENZL),ENZL
                    NASDAQ Equity,iShares MSCI Qatar ETF (QAT),QAT
                    NASDAQ Equity,iShares MSCI Turkey ETF (TUR),TUR
                    NASDAQ Equity,iShares MSCI UAE ETF (UAE),UAE
                    NASDAQ Equity,iShares Nasdaq Biotechnology Index Fund (IBB),IBB
                    NASDAQ Equity,iShares PHLX SOX Semiconductor Sector Index Fund (SOXX),SOXX
                    NASDAQ Equity,iShares Preferred and Income Securities ETF (PFF),PFF
                    NASDAQ Equity,iShares Russell 1000 Pure U.S. Revenue ETF (AMCA),AMCA
                    NASDAQ Equity,iShares S&P Emerging Markets Infrastructure Index Fund (EMIF),EMIF
                    NASDAQ Equity,iShares S&P Global Clean Energy Index Fund (ICLN),ICLN
                    NASDAQ Equity,iShares S&P Global Timber & Forestry Index Fund (WOOD),WOOD
                    NASDAQ Equity,iShares S&P India Nifty 50 Index Fund (INDY),INDY
                    NASDAQ Equity,iShares S&P Small-Cap 600 Growth ETF (IJT),IJT
                    NASDAQ Equity,iShares Select Dividend ETF (DVY),DVY
                    NASDAQ Equity,iShares Short Treasury Bond ETF (SHV),SHV
                    NASDAQ Equity,iShares Short-Term Corporate Bond ETF (IGSB),IGSB
                    NASDAQ Equity,"Isramco, Inc. (ISRL)",ISRL
                    NASDAQ Equity,Itamar Medical Ltd. (ITMR),ITMR
                    NASDAQ Equity,"Iteris, Inc. (ITI)",ITI
                    NASDAQ Equity,Iterum Therapeutics plc (ITRM),ITRM
                    NASDAQ Equity,"Itron, Inc. (ITRI)",ITRI
                    NASDAQ Equity,Ituran Location and Control Ltd. (ITRN),ITRN
                    NASDAQ Equity,"IVERIC bio, Inc. (ISEE)",ISEE
                    NASDAQ Equity,Ivy NextShares (IVENC),IVENC
                    NASDAQ Equity,Ivy NextShares (IVFGC),IVFGC
                    NASDAQ Equity,Ivy NextShares (IVFVC),IVFVC
                    NASDAQ Equity,"IZEA Worldwide, Inc. (IZEA)",IZEA
                    NASDAQ Equity,J & J Snack Foods Corp. (JJSF),JJSF
                    NASDAQ Equity,"J. W. Mays, Inc. (MAYS)",MAYS
                    NASDAQ Equity,"J.B. Hunt Transport Services, Inc. (JBHT)",JBHT
                    NASDAQ Equity,"j2 Global, Inc. (JCOM)",JCOM
                    NASDAQ Equity,"Jack Henry & Associates, Inc. (JKHY)",JKHY
                    NASDAQ Equity,Jack In The Box Inc. (JACK),JACK
                    NASDAQ Equity,"Jaguar Health, Inc. (JAGX)",JAGX
                    NASDAQ Equity,"JAKKS Pacific, Inc. (JAKK)",JAKK
                    NASDAQ Equity,"James River Group Holdings, Ltd. (JRVR)",JRVR
                    NASDAQ Equity,Janus Henderson Small Cap Growth Alpha ETF (JSML),JSML
                    NASDAQ Equity,Janus Henderson Small/Mid Cap Growth Alpha ETF (JSMD),JSMD
                    NASDAQ Equity,"Jason Industries, Inc. (JASN)",JASN
                    NASDAQ Equity,"Jason Industries, Inc. (JASNW)",JASNW
                    NASDAQ Equity,Jazz Pharmaceuticals plc (JAZZ),JAZZ
                    NASDAQ Equity,"JD.com, Inc. (JD)",JD
                    NASDAQ Equity,"Jerash Holdings (US), Inc. (JRSH)",JRSH
                    NASDAQ Equity,JetBlue Airways Corporation (JBLU),JBLU
                    NASDAQ Equity,Jewett-Cameron Trading Company (JCTCF),JCTCF
                    NASDAQ Equity,Jiayin Group Inc. (JFIN),JFIN
                    NASDAQ Equity,JMU Limited (JMU),JMU
                    NASDAQ Equity,"John B. Sanfilippo & Son, Inc. (JBSS)",JBSS
                    NASDAQ Equity,Johnson Outdoors Inc. (JOUT),JOUT
                    NASDAQ Equity,"Jounce Therapeutics, Inc. (JNCE)",JNCE
                    NASDAQ Equity,Kaiser Aluminum Corporation (KALU),KALU
                    NASDAQ Equity,Kaixin Auto Holdings (KXIN),KXIN
                    NASDAQ Equity,"Kala Pharmaceuticals, Inc. (KALA)",KALA
                    NASDAQ Equity,"Kaleido Biosciences, Inc. (KLDO)",KLDO
                    NASDAQ Equity,"KalVista Pharmaceuticals, Inc. (KALV)",KALV
                    NASDAQ Equity,Kamada Ltd. (KMDA),KMDA
                    NASDAQ Equity,"Kandi Technologies Group, Inc. (KNDI)",KNDI
                    NASDAQ Equity,Karyopharm Therapeutics Inc. (KPTI),KPTI
                    NASDAQ Equity,Kazia Therapeutics Limited (KZIA),KZIA
                    NASDAQ Equity,KBL Merger Corp. IV (KBLM),KBLM
                    NASDAQ Equity,KBL Merger Corp. IV (KBLMR),KBLMR
                    NASDAQ Equity,KBL Merger Corp. IV (KBLMU),KBLMU
                    NASDAQ Equity,KBL Merger Corp. IV (KBLMW),KBLMW
                    NASDAQ Equity,KBS Fashion Group Limited (KBSF),KBSF
                    NASDAQ Equity,Kearny Financial (KRNY),KRNY
                    NASDAQ Equity,"Kelly Services, Inc. (KELYA)",KELYA
                    NASDAQ Equity,"Kelly Services, Inc. (KELYB)",KELYB
                    NASDAQ Equity,"KemPharm, Inc. (KMPH)",KMPH
                    NASDAQ Equity,Kentucky First Federal Bancorp (KFFB),KFFB
                    NASDAQ Equity,Kewaunee Scientific Corporation (KEQU),KEQU
                    NASDAQ Equity,Key Tronic Corporation (KTCC),KTCC
                    NASDAQ Equity,"Kezar Life Sciences, Inc. (KZR)",KZR
                    NASDAQ Equity,"Kforce, Inc. (KFRC)",KFRC
                    NASDAQ Equity,"Kimball Electronics, Inc. (KE)",KE
                    NASDAQ Equity,"Kimball International, Inc. (KBAL)",KBAL
                    NASDAQ Equity,"Kindred Biosciences, Inc. (KIN)",KIN
                    NASDAQ Equity,Kingold Jewelry Inc. (KGJI),KGJI
                    NASDAQ Equity,"Kingstone Companies, Inc (KINS)",KINS
                    NASDAQ Equity,"Kiniksa Pharmaceuticals, Ltd. (KNSA)",KNSA
                    NASDAQ Equity,"Kinsale Capital Group, Inc. (KNSL)",KNSL
                    NASDAQ Equity,"Kirkland&#39;s, Inc. (KIRK)",KIRK
                    NASDAQ Equity,Kitov Pharma Ltd. (KTOV),KTOV
                    NASDAQ Equity,Kitov Pharma Ltd. (KTOVW),KTOVW
                    NASDAQ Equity,KLA-Tencor Corporation (KLAC),KLAC
                    NASDAQ Equity,"KLX Energy Services Holdings, Inc.  (KLXE)",KLXE
                    NASDAQ Equity,Kodiak Sciences Inc (KOD),KOD
                    NASDAQ Equity,Kopin Corporation (KOPN),KOPN
                    NASDAQ Equity,Kornit Digital Ltd. (KRNT),KRNT
                    NASDAQ Equity,Koss Corporation (KOSS),KOSS
                    NASDAQ Equity,KraneShares Trust KraneShares CSI China Internet ETF (KWEB),KWEB
                    NASDAQ Equity,"Kratos Defense & Security Solutions, Inc. (KTOS)",KTOS
                    NASDAQ Equity,"Krystal Biotech, Inc. (KRYS)",KRYS
                    NASDAQ Equity,"Kulicke and Soffa Industries, Inc. (KLIC)",KLIC
                    NASDAQ Equity,"Kura Oncology, Inc. (KURA)",KURA
                    NASDAQ Equity,"KVH Industries, Inc. (KVHI)",KVHI
                    NASDAQ Equity,L.B. Foster Company (FSTR),FSTR
                    NASDAQ Equity,La Jolla Pharmaceutical Company (LJPC),LJPC
                    NASDAQ Equity,"Lake Shore Bancorp, Inc. (LSBK)",LSBK
                    NASDAQ Equity,"Lakeland Bancorp, Inc. (LBAI)",LBAI
                    NASDAQ Equity,Lakeland Financial Corporation (LKFN),LKFN
                    NASDAQ Equity,"Lakeland Industries, Inc. (LAKE)",LAKE
                    NASDAQ Equity,Lam Research Corporation (LRCX),LRCX
                    NASDAQ Equity,Lamar Advertising Company (LAMR),LAMR
                    NASDAQ Equity,Lancaster Colony Corporation (LANC),LANC
                    NASDAQ Equity,"Landcadia Holdings II, Inc. (LCA)",LCA
                    NASDAQ Equity,"Landcadia Holdings II, Inc. (LCAHU)",LCAHU
                    NASDAQ Equity,"Landcadia Holdings II, Inc. (LCAHW)",LCAHW
                    NASDAQ Equity,Landec Corporation (LNDC),LNDC
                    NASDAQ Equity,Landmark Bancorp Inc. (LARK),LARK
                    NASDAQ Equity,Landmark Infrastructure Partners LP (LMRK),LMRK
                    NASDAQ Equity,Landmark Infrastructure Partners LP (LMRKN),LMRKN
                    NASDAQ Equity,Landmark Infrastructure Partners LP (LMRKO),LMRKO
                    NASDAQ Equity,Landmark Infrastructure Partners LP (LMRKP),LMRKP
                    NASDAQ Equity,"Lands&#39; End, Inc. (LE)",LE
                    NASDAQ Equity,"Landstar System, Inc. (LSTR)",LSTR
                    NASDAQ Equity,"Lantheus Holdings, Inc. (LNTH)",LNTH
                    NASDAQ Equity,"Lantronix, Inc. (LTRX)",LTRX
                    NASDAQ Equity,Lattice Semiconductor Corporation (LSCC),LSCC
                    NASDAQ Equity,"Laureate Education, Inc. (LAUR)",LAUR
                    NASDAQ Equity,"Lawson Products, Inc. (LAWS)",LAWS
                    NASDAQ Equity,"Lazydays Holdings, Inc. (LAZY)",LAZY
                    NASDAQ Equity,LCNB Corporation (LCNB),LCNB
                    NASDAQ Equity,"LEAP THERAPEUTICS, INC. (LPTX)",LPTX
                    NASDAQ Equity,Legacy Housing Corporation (LEGH),LEGH
                    NASDAQ Equity,Legacy Reserves Inc. (LGCY),LGCY
                    NASDAQ Equity,"LegacyTexas Financial Group, Inc. (LTXB)",LTXB
                    NASDAQ Equity,Legg Mason Global Infrastructure ETF (INFR),INFR
                    NASDAQ Equity,Legg Mason Low Volatility High Dividend ETF (LVHD),LVHD
                    NASDAQ Equity,Legg Mason Small-Cap Quality Value ETF (SQLV),SQLV
                    NASDAQ Equity,Leisure Acquisition Corp. (LACQ),LACQ
                    NASDAQ Equity,Leisure Acquisition Corp. (LACQU),LACQU
                    NASDAQ Equity,Leisure Acquisition Corp. (LACQW),LACQW
                    NASDAQ Equity,"LeMaitre Vascular, Inc. (LMAT)",LMAT
                    NASDAQ Equity,"LendingTree, Inc. (TREE)",TREE
                    NASDAQ Equity,"Level One Bancorp, Inc. (LEVL)",LEVL
                    NASDAQ Equity,"Lexicon Pharmaceuticals, Inc. (LXRX)",LXRX
                    NASDAQ Equity,LexinFintech Holdings Ltd. (LX),LX
                    NASDAQ Equity,LF Capital Acquistion Corp. (LFAC),LFAC
                    NASDAQ Equity,LF Capital Acquistion Corp. (LFACU),LFACU
                    NASDAQ Equity,LF Capital Acquistion Corp. (LFACW),LFACW
                    NASDAQ Equity,"LGI Homes, Inc. (LGIH)",LGIH
                    NASDAQ Equity,LHC Group (LHCG),LHCG
                    NASDAQ Equity,Lianluo Smart Limited (LLIT),LLIT
                    NASDAQ Equity,Liberty Broadband Corporation (LBRDA),LBRDA
                    NASDAQ Equity,Liberty Broadband Corporation (LBRDK),LBRDK
                    NASDAQ Equity,"Liberty Expedia Holdings, Inc. (LEXEA)",LEXEA
                    NASDAQ Equity,"Liberty Expedia Holdings, Inc. (LEXEB)",LEXEB
                    NASDAQ Equity,Liberty Global plc (LBTYA),LBTYA
                    NASDAQ Equity,Liberty Global plc (LBTYB),LBTYB
                    NASDAQ Equity,Liberty Global plc (LBTYK),LBTYK
                    NASDAQ Equity,Liberty Latin America Ltd. (LILA),LILA
                    NASDAQ Equity,Liberty Latin America Ltd. (LILAK),LILAK
                    NASDAQ Equity,Liberty Media Corporation (BATRA),BATRA
                    NASDAQ Equity,Liberty Media Corporation (BATRK),BATRK
                    NASDAQ Equity,Liberty Media Corporation (FWONA),FWONA
                    NASDAQ Equity,Liberty Media Corporation (FWONK),FWONK
                    NASDAQ Equity,Liberty Media Corporation (LSXMA),LSXMA
                    NASDAQ Equity,Liberty Media Corporation (LSXMB),LSXMB
                    NASDAQ Equity,Liberty Media Corporation (LSXMK),LSXMK
                    NASDAQ Equity,"Liberty TripAdvisor Holdings, Inc. (LTRPA)",LTRPA
                    NASDAQ Equity,"Liberty TripAdvisor Holdings, Inc. (LTRPB)",LTRPB
                    NASDAQ Equity,"Lifetime Brands, Inc. (LCUT)",LCUT
                    NASDAQ Equity,Lifevantage Corporation (LFVN),LFVN
                    NASDAQ Equity,"Lifeway Foods, Inc. (LWAY)",LWAY
                    NASDAQ Equity,Ligand Pharmaceuticals Incorporated (LGND),LGND
                    NASDAQ Equity,Lightbridge Corporation (LTBR),LTBR
                    NASDAQ Equity,"LightPath Technologies, Inc. (LPTH)",LPTH
                    NASDAQ Equity,"Lilis Energy, Inc. (LLEX)",LLEX
                    NASDAQ Equity,"Limbach Holdings, Inc. (LMB)",LMB
                    NASDAQ Equity,"Limelight Networks, Inc. (LLNW)",LLNW
                    NASDAQ Equity,"Limestone Bancorp, Inc. (LMST)",LMST
                    NASDAQ Equity,Limoneira Co (LMNR),LMNR
                    NASDAQ Equity,Lincoln Educational Services Corporation (LINC),LINC
                    NASDAQ Equity,"Lincoln Electric Holdings, Inc. (LECO)",LECO
                    NASDAQ Equity,Lindblad Expeditions Holdings Inc.  (LIND),LIND
                    NASDAQ Equity,Lindblad Expeditions Holdings Inc.  (LINDW),LINDW
                    NASDAQ Equity,Lipocine Inc. (LPCN),LPCN
                    NASDAQ Equity,"LiqTech International, Inc. (LIQT)",LIQT
                    NASDAQ Equity,Liquid Media Group Ltd. (YVR),YVR
                    NASDAQ Equity,"Liquidia Technologies, Inc. (LQDA)",LQDA
                    NASDAQ Equity,"Liquidity Services, Inc. (LQDT)",LQDT
                    NASDAQ Equity,"Littelfuse, Inc. (LFUS)",LFUS
                    NASDAQ Equity,LivaNova PLC (LIVN),LIVN
                    NASDAQ Equity,"Live Oak Bancshares, Inc. (LOB)",LOB
                    NASDAQ Equity,Live Ventures Incorporated (LIVE),LIVE
                    NASDAQ Equity,"LivePerson, Inc. (LPSN)",LPSN
                    NASDAQ Equity,"LiveXLive Media, Inc. (LIVX)",LIVX
                    NASDAQ Equity,LKQ Corporation (LKQ),LKQ
                    NASDAQ Equity,"LM Funding America, Inc. (LMFA)",LMFA
                    NASDAQ Equity,"LM Funding America, Inc. (LMFAW)",LMFAW
                    NASDAQ Equity,"LogicBio Therapeutics, Inc. (LOGC)",LOGC
                    NASDAQ Equity,Logitech International S.A. (LOGI),LOGI
                    NASDAQ Equity,"LogMein, Inc. (LOGM)",LOGM
                    NASDAQ Equity,Loncar Cancer Immunotherapy ETF (CNCR),CNCR
                    NASDAQ Equity,Loncar China BioPharma ETF (CHNA),CHNA
                    NASDAQ Equity,Lonestar Resources US Inc. (LONE),LONE
                    NASDAQ Equity,Longevity Acquisition Corporation (LOAC),LOAC
                    NASDAQ Equity,Longevity Acquisition Corporation (LOACR),LOACR
                    NASDAQ Equity,Longevity Acquisition Corporation (LOACU),LOACU
                    NASDAQ Equity,Longevity Acquisition Corporation (LOACW),LOACW
                    NASDAQ Equity,"Loop Industries, Inc. (LOOP)",LOOP
                    NASDAQ Equity,"Loral Space and Communications, Inc. (LORL)",LORL
                    NASDAQ Equity,LPL Financial Holdings Inc. (LPLA),LPLA
                    NASDAQ Equity,LRAD Corporation (LRAD),LRAD
                    NASDAQ Equity,LSI Industries Inc. (LYTS),LYTS
                    NASDAQ Equity,Luckin Coffee Inc. (LK),LK
                    NASDAQ Equity,lululemon athletica inc. (LULU),LULU
                    NASDAQ Equity,Lumentum Holdings Inc. (LITE),LITE
                    NASDAQ Equity,Luminex Corporation (LMNX),LMNX
                    NASDAQ Equity,Luna Innovations Incorporated (LUNA),LUNA
                    NASDAQ Equity,Luokung Technology Corp (LKCO),LKCO
                    NASDAQ Equity,Luther Burbank Corporation (LBC),LBC
                    NASDAQ Equity,"Lyft, Inc. (LYFT)",LYFT
                    NASDAQ Equity,M B T Financial Corp (MBTF),MBTF
                    NASDAQ Equity,Macatawa Bank Corporation (MCBC),MCBC
                    NASDAQ Equity,Mackinac Financial Corporation (MFNC),MFNC
                    NASDAQ Equity,"MACOM Technology Solutions Holdings, Inc. (MTSI)",MTSI
                    NASDAQ Equity,"MacroGenics, Inc. (MGNX)",MGNX
                    NASDAQ Equity,"Madrigal Pharmaceuticals, Inc. (MDGL)",MDGL
                    NASDAQ Equity,Magal Security Systems Ltd. (MAGS),MAGS
                    NASDAQ Equity,"Magellan Health, Inc. (MGLN)",MGLN
                    NASDAQ Equity,"Magenta Therapeutics, Inc. (MGTA)",MGTA
                    NASDAQ Equity,Magic Software Enterprises Ltd. (MGIC),MGIC
                    NASDAQ Equity,"Magyar Bancorp, Inc. (MGYR)",MGYR
                    NASDAQ Equity,"Maiden Holdings, Ltd. (MHLD)",MHLD
                    NASDAQ Equity,"MainStreet Bancshares, Inc. (MNSB)",MNSB
                    NASDAQ Equity,Majesco (MJCO),MJCO
                    NASDAQ Equity,MakeMyTrip Limited (MMYT),MMYT
                    NASDAQ Equity,"Malibu Boats, Inc. (MBUU)",MBUU
                    NASDAQ Equity,"Malvern Bancorp, Inc. (MLVF)",MLVF
                    NASDAQ Equity,"MAM Software Group, Inc. (MAMS)",MAMS
                    NASDAQ Equity,"Mammoth Energy Services, Inc. (TUSK)",TUSK
                    NASDAQ Equity,"Manhattan Associates, Inc. (MANH)",MANH
                    NASDAQ Equity,"Manhattan Bridge Capital, Inc (LOAN)",LOAN
                    NASDAQ Equity,"Manitex International, Inc. (MNTX)",MNTX
                    NASDAQ Equity,"Mannatech, Incorporated (MTEX)",MTEX
                    NASDAQ Equity,MannKind Corporation (MNKD),MNKD
                    NASDAQ Equity,ManTech International Corporation (MANT),MANT
                    NASDAQ Equity,"Marathon Patent Group, Inc. (MARA)",MARA
                    NASDAQ Equity,"Marchex, Inc. (MCHX)",MCHX
                    NASDAQ Equity,Marin Software Incorporated (MRIN),MRIN
                    NASDAQ Equity,Marine Petroleum Trust (MARPS),MARPS
                    NASDAQ Equity,"Marinus Pharmaceuticals, Inc. (MRNS)",MRNS
                    NASDAQ Equity,"Marker Therapeutics, Inc. (MRKR)",MRKR
                    NASDAQ Equity,"MarketAxess Holdings, Inc. (MKTX)",MKTX
                    NASDAQ Equity,Marlin Business Services Corp. (MRLN),MRLN
                    NASDAQ Equity,Marriott International (MAR),MAR
                    NASDAQ Equity,"Marrone Bio Innovations, Inc. (MBII)",MBII
                    NASDAQ Equity,"Marten Transport, Ltd. (MRTN)",MRTN
                    NASDAQ Equity,Martin Midstream Partners L.P. (MMLP),MMLP
                    NASDAQ Equity,Marvell Technology Group Ltd. (MRVL),MRVL
                    NASDAQ Equity,Masimo Corporation (MASI),MASI
                    NASDAQ Equity,"MasterCraft Boat Holdings, Inc. (MCFT)",MCFT
                    NASDAQ Equity,"Match Group, Inc. (MTCH)",MTCH
                    NASDAQ Equity,Materialise NV (MTLS),MTLS
                    NASDAQ Equity,Matrix Service Company (MTRX),MTRX
                    NASDAQ Equity,"Mattel, Inc. (MAT)",MAT
                    NASDAQ Equity,Matthews International Corporation (MATW),MATW
                    NASDAQ Equity,"Maxim Integrated Products, Inc. (MXIM)",MXIM
                    NASDAQ Equity,McGrath RentCorp (MGRC),MGRC
                    NASDAQ Equity,MDC Partners Inc. (MDCA),MDCA
                    NASDAQ Equity,MDJM LTD (MDJH),MDJH
                    NASDAQ Equity,"Medalist Diversified REIT, Inc. (MDRR)",MDRR
                    NASDAQ Equity,Medallion Financial Corp. (MFIN),MFIN
                    NASDAQ Equity,Medallion Financial Corp. (MFINL),MFINL
                    NASDAQ Equity,"MediciNova, Inc. (MNOV)",MNOV
                    NASDAQ Equity,"Medidata Solutions, Inc. (MDSO)",MDSO
                    NASDAQ Equity,Medigus Ltd. (MDGS),MDGS
                    NASDAQ Equity,Medigus Ltd. (MDGSW),MDGSW
                    NASDAQ Equity,MediWound Ltd. (MDWD),MDWD
                    NASDAQ Equity,"Medpace Holdings, Inc. (MEDP)",MEDP
                    NASDAQ Equity,"MEI Pharma, Inc. (MEIP)",MEIP
                    NASDAQ Equity,MeiraGTx Holdings plc (MGTX),MGTX
                    NASDAQ Equity,Melco Resorts & Entertainment Limited (MLCO),MLCO
                    NASDAQ Equity,"Melinta Therapeutics, Inc. (MLNT)",MLNT
                    NASDAQ Equity,"Mellanox Technologies, Ltd. (MLNX)",MLNX
                    NASDAQ Equity,"Melrose Bancorp, Inc. (MELR)",MELR
                    NASDAQ Equity,Menlo Therapeutics Inc. (MNLO),MNLO
                    NASDAQ Equity,MER Telemanagement Solutions Ltd. (MTSL),MTSL
                    NASDAQ Equity,"MercadoLibre, Inc. (MELI)",MELI
                    NASDAQ Equity,Mercantile Bank Corporation (MBWM),MBWM
                    NASDAQ Equity,Mercer International Inc. (MERC),MERC
                    NASDAQ Equity,Merchants Bancorp (MBIN),MBIN
                    NASDAQ Equity,Merchants Bancorp (MBINP),MBINP
                    NASDAQ Equity,Mercury Systems Inc (MRCY),MRCY
                    NASDAQ Equity,Mereo BioPharma Group plc (MREO),MREO
                    NASDAQ Equity,"Meridian Bancorp, Inc. (EBSB)",EBSB
                    NASDAQ Equity,Meridian Bioscience Inc. (VIVO),VIVO
                    NASDAQ Equity,Meridian Corporation (MRBK),MRBK
                    NASDAQ Equity,"Merit Medical Systems, Inc. (MMSI)",MMSI
                    NASDAQ Equity,"Merrimack Pharmaceuticals, Inc. (MACK)",MACK
                    NASDAQ Equity,"Mersana Therapeutics, Inc. (MRSN)",MRSN
                    NASDAQ Equity,Merus N.V. (MRUS),MRUS
                    NASDAQ Equity,"Mesa Air Group, Inc. (MESA)",MESA
                    NASDAQ Equity,"Mesa Laboratories, Inc. (MLAB)",MLAB
                    NASDAQ Equity,Mesoblast Limited (MESO),MESO
                    NASDAQ Equity,"Meta Financial Group, Inc. (CASH)",CASH
                    NASDAQ Equity,Methanex Corporation (MEOH),MEOH
                    NASDAQ Equity,MGE Energy Inc. (MGEE),MGEE
                    NASDAQ Equity,"MGP Ingredients, Inc. (MGPI)",MGPI
                    NASDAQ Equity,Microbot Medical Inc.  (MBOT),MBOT
                    NASDAQ Equity,Microchip Technology Incorporated (MCHP),MCHP
                    NASDAQ Equity,"Micron Technology, Inc. (MU)",MU
                    NASDAQ Equity,Microsoft Corporation (MSFT),MSFT
                    NASDAQ Equity,MicroStrategy Incorporated (MSTR),MSTR
                    NASDAQ Equity,"Microvision, Inc. (MVIS)",MVIS
                    NASDAQ Equity,"MICT, Inc. (MICT)",MICT
                    NASDAQ Equity,Mid Penn Bancorp (MPB),MPB
                    NASDAQ Equity,Midatech Pharma PLC (MTP),MTP
                    NASDAQ Equity,"Mid-Con Energy Partners, LP (MCEP)",MCEP
                    NASDAQ Equity,Middlefield Banc Corp. (MBCN),MBCN
                    NASDAQ Equity,Middlesex Water Company (MSEX),MSEX
                    NASDAQ Equity,"Midland States Bancorp, Inc. (MSBI)",MSBI
                    NASDAQ Equity,"Mid-Southern Bancorp, Inc. (MSVB)",MSVB
                    NASDAQ Equity,"MidWestOne Financial Group, Inc. (MOFG)",MOFG
                    NASDAQ Equity,Milestone Pharmaceuticals Inc. (MIST),MIST
                    NASDAQ Equity,"Millendo Therapeutics, Inc.  (MLND)",MLND
                    NASDAQ Equity,Millicom International Cellular S.A. (TIGO),TIGO
                    NASDAQ Equity,Mimecast Limited (MIME),MIME
                    NASDAQ Equity,MIND C.T.I. Ltd. (MNDO),MNDO
                    NASDAQ Equity,"Minerva Neurosciences, Inc (NERV)",NERV
                    NASDAQ Equity,"Miragen Therapeutics, Inc. (MGEN)",MGEN
                    NASDAQ Equity,"Mirati Therapeutics, Inc. (MRTX)",MRTX
                    NASDAQ Equity,"MISONIX, Inc. (MSON)",MSON
                    NASDAQ Equity,"Mitcham Industries, Inc. (MIND)",MIND
                    NASDAQ Equity,"Mitcham Industries, Inc. (MINDP)",MINDP
                    NASDAQ Equity,"Mitek Systems, Inc. (MITK)",MITK
                    NASDAQ Equity,"MKS Instruments, Inc. (MKSI)",MKSI
                    NASDAQ Equity,"MMA Capital Holdings, Inc. (MMAC)",MMAC
                    NASDAQ Equity,"MMTec, Inc. (MTC)",MTC
                    NASDAQ Equity,"Mobile Mini, Inc. (MINI)",MINI
                    NASDAQ Equity,"MobileIron, Inc. (MOBL)",MOBL
                    NASDAQ Equity,Modern Media Acquisition Corp. (MMDM),MMDM
                    NASDAQ Equity,Modern Media Acquisition Corp. (MMDMR),MMDMR
                    NASDAQ Equity,Modern Media Acquisition Corp. (MMDMU),MMDMU
                    NASDAQ Equity,Modern Media Acquisition Corp. (MMDMW),MMDMW
                    NASDAQ Equity,"Moderna, Inc. (MRNA)",MRNA
                    NASDAQ Equity,Mogo Inc. (MOGO),MOGO
                    NASDAQ Equity,"Mohawk Group Holdings, Inc. (MWK)",MWK
                    NASDAQ Equity,"Molecular Templates, Inc. (MTEM)",MTEM
                    NASDAQ Equity,"Moleculin Biotech, Inc. (MBRX)",MBRX
                    NASDAQ Equity,"Momenta Pharmaceuticals, Inc. (MNTA)",MNTA
                    NASDAQ Equity,Momo Inc. (MOMO),MOMO
                    NASDAQ Equity,"Monaker Group, Inc. (MKGI)",MKGI
                    NASDAQ Equity,"Monarch Casino & Resort, Inc. (MCRI)",MCRI
                    NASDAQ Equity,"Mondelez International, Inc. (MDLZ)",MDLZ
                    NASDAQ Equity,"Moneygram International, Inc. (MGI)",MGI
                    NASDAQ Equity,"MongoDB, Inc. (MDB)",MDB
                    NASDAQ Equity,Monocle Acquisition Corporation (MNCL),MNCL
                    NASDAQ Equity,Monocle Acquisition Corporation (MNCLU),MNCLU
                    NASDAQ Equity,Monocle Acquisition Corporation (MNCLW),MNCLW
                    NASDAQ Equity,"Monolithic Power Systems, Inc. (MPWR)",MPWR
                    NASDAQ Equity,Monotype Imaging Holdings Inc. (TYPE),TYPE
                    NASDAQ Equity,"Monro, Inc.  (MNRO)",MNRO
                    NASDAQ Equity,Monroe Capital Corporation (MRCC),MRCC
                    NASDAQ Equity,Monroe Capital Corporation (MRCCL),MRCCL
                    NASDAQ Equity,Monster Beverage Corporation (MNST),MNST
                    NASDAQ Equity,"Morningstar, Inc. (MORN)",MORN
                    NASDAQ Equity,MorphoSys AG (MOR),MOR
                    NASDAQ Equity,"MoSys, Inc. (MOSY)",MOSY
                    NASDAQ Equity,Motif Bio plc (MTFB),MTFB
                    NASDAQ Equity,Motif Bio plc (MTFBW),MTFBW
                    NASDAQ Equity,"Motorcar Parts of America, Inc. (MPAA)",MPAA
                    NASDAQ Equity,"Motus GI Holdings, Inc. (MOTS)",MOTS
                    NASDAQ Equity,Mountain Province Diamonds Inc. (MPVD),MPVD
                    NASDAQ Equity,"Moxian, Inc. (MOXC)",MOXC
                    NASDAQ Equity,Mr. Cooper Group Inc. (COOP),COOP
                    NASDAQ Equity,MSB Financial Corp. (MSBF),MSBF
                    NASDAQ Equity,"MTBC, Inc. (MTBC)",MTBC
                    NASDAQ Equity,"MTBC, Inc. (MTBCP)",MTBCP
                    NASDAQ Equity,MTS Systems Corporation (MTSC),MTSC
                    NASDAQ Equity,Mudrick Capital Acquisition Corporation (MUDS),MUDS
                    NASDAQ Equity,Mudrick Capital Acquisition Corporation (MUDSU),MUDSU
                    NASDAQ Equity,Mudrick Capital Acquisition Corporation (MUDSW),MUDSW
                    NASDAQ Equity,Multi-Color Corporation (LABL),LABL
                    NASDAQ Equity,"Mustang Bio, Inc. (MBIO)",MBIO
                    NASDAQ Equity,MutualFirst Financial Inc. (MFSF),MFSF
                    NASDAQ Equity,MVB Financial Corp. (MVBF),MVBF
                    NASDAQ Equity,"My Size, Inc. (MYSZ)",MYSZ
                    NASDAQ Equity,Mylan N.V. (MYL),MYL
                    NASDAQ Equity,"MYnd Analytics, Inc. (MYND)",MYND
                    NASDAQ Equity,"MYnd Analytics, Inc. (MYNDW)",MYNDW
                    NASDAQ Equity,"MyoKardia, Inc. (MYOK)",MYOK
                    NASDAQ Equity,MYOS RENS Technology Inc. (MYOS),MYOS
                    NASDAQ Equity,"MYR Group, Inc. (MYRG)",MYRG
                    NASDAQ Equity,"Myriad Genetics, Inc. (MYGN)",MYGN
                    NASDAQ Equity,Nabriva Therapeutics plc (NBRV),NBRV
                    NASDAQ Equity,Naked Brand Group Limited (NAKD),NAKD
                    NASDAQ Equity,Nano Dimension Ltd. (NNDM),NNDM
                    NASDAQ Equity,Nanometrics Incorporated (NANO),NANO
                    NASDAQ Equity,"NanoString Technologies, Inc. (NSTG)",NSTG
                    NASDAQ Equity,"NanoVibronix, Inc. (NAOV)",NAOV
                    NASDAQ Equity,"NantHealth, Inc. (NH)",NH
                    NASDAQ Equity,"NantKwest, Inc. (NK)",NK
                    NASDAQ Equity,"NAPCO Security Technologies, Inc. (NSSC)",NSSC
                    NASDAQ Equity,"Nasdaq, Inc. (NDAQ)",NDAQ
                    NASDAQ Equity,"Natera, Inc. (NTRA)",NTRA
                    NASDAQ Equity,"Nathan&#39;s Famous, Inc. (NATH)",NATH
                    NASDAQ Equity,"National Bankshares, Inc. (NKSH)",NKSH
                    NASDAQ Equity,National Beverage Corp. (FIZZ),FIZZ
                    NASDAQ Equity,"National CineMedia, Inc. (NCMI)",NCMI
                    NASDAQ Equity,National Energy Services Reunited Corp. (NESR),NESR
                    NASDAQ Equity,National Energy Services Reunited Corp. (NESRW),NESRW
                    NASDAQ Equity,National General Holdings Corp (NGHC),NGHC
                    NASDAQ Equity,National General Holdings Corp (NGHCN),NGHCN
                    NASDAQ Equity,National General Holdings Corp (NGHCO),NGHCO
                    NASDAQ Equity,National General Holdings Corp (NGHCP),NGHCP
                    NASDAQ Equity,National General Holdings Corp (NGHCZ),NGHCZ
                    NASDAQ Equity,National Holdings Corporation (NHLD),NHLD
                    NASDAQ Equity,National Holdings Corporation (NHLDW),NHLDW
                    NASDAQ Equity,National Instruments Corporation (NATI),NATI
                    NASDAQ Equity,National Research Corporation (NRC),NRC
                    NASDAQ Equity,"National Security Group, Inc. (NSEC)",NSEC
                    NASDAQ Equity,"National Vision Holdings, Inc. (EYE)",EYE
                    NASDAQ Equity,"National Western Life Group, Inc. (NWLI)",NWLI
                    NASDAQ Equity,"Natural Alternatives International, Inc. (NAII)",NAII
                    NASDAQ Equity,Natural Health Trends Corp. (NHTC),NHTC
                    NASDAQ Equity,"Nature&#39;s Sunshine Products, Inc. (NATR)",NATR
                    NASDAQ Equity,Natus Medical Incorporated (BABY),BABY
                    NASDAQ Equity,Navient Corporation (JSM),JSM
                    NASDAQ Equity,Navient Corporation (NAVI),NAVI
                    NASDAQ Equity,Navios Maritime Containers L.P. (NMCI),NMCI
                    NASDAQ Equity,NBT Bancorp Inc. (NBTB),NBTB
                    NASDAQ Equity,"NCS Multistage Holdings, Inc. (NCSM)",NCSM
                    NASDAQ Equity,Nebula Acquisition Corporation (NEBU),NEBU
                    NASDAQ Equity,Nebula Acquisition Corporation (NEBUU),NEBUU
                    NASDAQ Equity,Nebula Acquisition Corporation (NEBUW),NEBUW
                    NASDAQ Equity,Nektar Therapeutics (NKTR),NKTR
                    NASDAQ Equity,Nemaura Medical Inc. (NMRD),NMRD
                    NASDAQ Equity,Neogen Corporation (NEOG),NEOG
                    NASDAQ Equity,"NeoGenomics, Inc. (NEO)",NEO
                    NASDAQ Equity,"Neon Therapeutics, Inc. (NTGN)",NTGN
                    NASDAQ Equity,Neonode Inc. (NEON),NEON
                    NASDAQ Equity,"Neos Therapeutics, Inc. (NEOS)",NEOS
                    NASDAQ Equity,Neovasc Inc. (NVCN),NVCN
                    NASDAQ Equity,Neptune Wellness Solutions Inc. (NEPT),NEPT
                    NASDAQ Equity,"Net 1 UEPS Technologies, Inc. (UEPS)",UEPS
                    NASDAQ Equity,"Net Element, Inc. (NETE)",NETE
                    NASDAQ Equity,"NetApp, Inc. (NTAP)",NTAP
                    NASDAQ Equity,"NetEase, Inc. (NTES)",NTES
                    NASDAQ Equity,"Netflix, Inc. (NFLX)",NFLX
                    NASDAQ Equity,"NETGEAR, Inc. (NTGR)",NTGR
                    NASDAQ Equity,"NetScout Systems, Inc. (NTCT)",NTCT
                    NASDAQ Equity,NetSol Technologies Inc. (NTWK),NTWK
                    NASDAQ Equity,"Neuralstem, Inc. (CUR)",CUR
                    NASDAQ Equity,"Neurocrine Biosciences, Inc. (NBIX)",NBIX
                    NASDAQ Equity,"NeuroMetrix, Inc. (NURO)",NURO
                    NASDAQ Equity,"NeuroMetrix, Inc. (NUROW)",NUROW
                    NASDAQ Equity,"Neuronetics, Inc. (STIM)",STIM
                    NASDAQ Equity,"Neurotrope, Inc. (NTRP)",NTRP
                    NASDAQ Equity,New Age Beverages Corporation (NBEV),NBEV
                    NASDAQ Equity,New Fortress Energy LLC (NFE),NFE
                    NASDAQ Equity,"New York Mortgage Trust, Inc. (NYMT)",NYMT
                    NASDAQ Equity,"New York Mortgage Trust, Inc. (NYMTN)",NYMTN
                    NASDAQ Equity,"New York Mortgage Trust, Inc. (NYMTO)",NYMTO
                    NASDAQ Equity,"New York Mortgage Trust, Inc. (NYMTP)",NYMTP
                    NASDAQ Equity,"Newater Technology, Inc. (NEWA)",NEWA
                    NASDAQ Equity,Newell Brands Inc. (NWL),NWL
                    NASDAQ Equity,NewLink Genetics Corporation (NLNK),NLNK
                    NASDAQ Equity,"Newmark Group, Inc. (NMRK)",NMRK
                    NASDAQ Equity,News Corporation (NWS),NWS
                    NASDAQ Equity,News Corporation (NWSA),NWSA
                    NASDAQ Equity,Newtek Business Services Corp. (NEWT),NEWT
                    NASDAQ Equity,Newtek Business Services Corp. (NEWTI),NEWTI
                    NASDAQ Equity,Newtek Business Services Corp. (NEWTZ),NEWTZ
                    NASDAQ Equity,"Nexstar Media Group, Inc. (NXST)",NXST
                    NASDAQ Equity,"NextCure, Inc. (NXTC)",NXTC
                    NASDAQ Equity,NextDecade Corporation (NEXT),NEXT
                    NASDAQ Equity,"NextGen Healthcare, Inc. (NXGN)",NXGN
                    NASDAQ Equity,NF Energy Saving Corporation (BIMI),BIMI
                    NASDAQ Equity,"NGM Biopharmaceuticals, Inc. (NGM)",NGM
                    NASDAQ Equity,"NI Holdings, Inc. (NODK)",NODK
                    NASDAQ Equity,NIC Inc. (EGOV),EGOV
                    NASDAQ Equity,NICE Ltd (NICE),NICE
                    NASDAQ Equity,"Nicholas Financial, Inc. (NICK)",NICK
                    NASDAQ Equity,Nicolet Bankshares Inc. (NCBS),NCBS
                    NASDAQ Equity,"NII Holdings, Inc. (NIHD)",NIHD
                    NASDAQ Equity,Niu Technologies (NIU),NIU
                    NASDAQ Equity,"nLIGHT, Inc. (LASR)",LASR
                    NASDAQ Equity,NMI Holdings Inc (NMIH),NMIH
                    NASDAQ Equity,"NN, Inc. (NNBR)",NNBR
                    NASDAQ Equity,Noodles & Company (NDLS),NDLS
                    NASDAQ Equity,Nordson Corporation (NDSN),NDSN
                    NASDAQ Equity,Nortech Systems Incorporated (NSYS),NSYS
                    NASDAQ Equity,Northeast Bank (NBN),NBN
                    NASDAQ Equity,Northern Technologies International Corporation (NTIC),NTIC
                    NASDAQ Equity,Northern Trust Corporation (NTRS),NTRS
                    NASDAQ Equity,Northern Trust Corporation (NTRSP),NTRSP
                    NASDAQ Equity,"Northfield Bancorp, Inc. (NFBK)",NFBK
                    NASDAQ Equity,Northrim BanCorp Inc (NRIM),NRIM
                    NASDAQ Equity,"Northwest Bancshares, Inc. (NWBI)",NWBI
                    NASDAQ Equity,Northwest Pipe Company (NWPX),NWPX
                    NASDAQ Equity,Norwegian Cruise Line Holdings Ltd. (NCLH),NCLH
                    NASDAQ Equity,Norwood Financial Corp. (NWFL),NWFL
                    NASDAQ Equity,"Nova Lifestyle, Inc (NVFY)",NVFY
                    NASDAQ Equity,Nova Measuring Instruments Ltd. (NVMI),NVMI
                    NASDAQ Equity,"Novan, Inc. (NOVN)",NOVN
                    NASDAQ Equity,Novanta Inc. (NOVT),NOVT
                    NASDAQ Equity,"Novavax, Inc. (NVAX)",NVAX
                    NASDAQ Equity,Novelion Therapeutics Inc.  (NVLN),NVLN
                    NASDAQ Equity,NovoCure Limited (NVCR),NVCR
                    NASDAQ Equity,"Novus Therapeutics, Inc. (NVUS)",NVUS
                    NASDAQ Equity,"Nuance Communications, Inc. (NUAN)",NUAN
                    NASDAQ Equity,NuCana plc (NCNA),NCNA
                    NASDAQ Equity,"Nutanix, Inc. (NTNX)",NTNX
                    NASDAQ Equity,"NuVasive, Inc. (NUVA)",NUVA
                    NASDAQ Equity,Nuvectra Corporation (NVTR),NVTR
                    NASDAQ Equity,Nuveen NASDAQ 100 Dynamic Overwrite Fund (QQQX),QQQX
                    NASDAQ Equity,"NV5 Global, Inc. (NVEE)",NVEE
                    NASDAQ Equity,NVE Corporation (NVEC),NVEC
                    NASDAQ Equity,NVIDIA Corporation (NVDA),NVDA
                    NASDAQ Equity,NXP Semiconductors N.V. (NXPI),NXPI
                    NASDAQ Equity,NXT-ID Inc. (NXTD),NXTD
                    NASDAQ Equity,NXT-ID Inc. (NXTDW),NXTDW
                    NASDAQ Equity,Nymox Pharmaceutical Corporation (NYMX),NYMX
                    NASDAQ Equity,O2Micro International Limited (OIIM),OIIM
                    NASDAQ Equity,Oak Valley Bancorp (CA) (OVLY),OVLY
                    NASDAQ Equity,Oaktree Specialty Lending Corporation (OCSL),OCSL
                    NASDAQ Equity,Oaktree Specialty Lending Corporation (OCSLL),OCSLL
                    NASDAQ Equity,Oaktree Strategic Income Corporation (OCSI),OCSI
                    NASDAQ Equity,Oasmia Pharmaceutical AB (OASM),OASM
                    NASDAQ Equity,"Obalon Therapeutics, Inc. (OBLN)",OBLN
                    NASDAQ Equity,ObsEva SA (OBSV),OBSV
                    NASDAQ Equity,"Ocean Bio-Chem, Inc. (OBCI)",OBCI
                    NASDAQ Equity,"Ocean Power Technologies, Inc. (OPTT)",OPTT
                    NASDAQ Equity,OceanFirst Financial Corp. (OCFC),OCFC
                    NASDAQ Equity,Oconee Federal Financial Corp. (OFED),OFED
                    NASDAQ Equity,"Ocular Therapeutix, Inc. (OCUL)",OCUL
                    NASDAQ Equity,"Odonate Therapeutics, Inc. (ODT)",ODT
                    NASDAQ Equity,"Odyssey Marine Exploration, Inc. (OMEX)",OMEX
                    NASDAQ Equity,"Office Depot, Inc. (ODP)",ODP
                    NASDAQ Equity,Office Properties Income Trust (OPI),OPI
                    NASDAQ Equity,Office Properties Income Trust (OPINI),OPINI
                    NASDAQ Equity,OFS Capital Corporation (OFS),OFS
                    NASDAQ Equity,OFS Capital Corporation (OFSSL),OFSSL
                    NASDAQ Equity,OFS Capital Corporation (OFSSZ),OFSSZ
                    NASDAQ Equity,"OFS Credit Company, Inc. (OCCI)",OCCI
                    NASDAQ Equity,"OFS Credit Company, Inc. (OCCIP)",OCCIP
                    NASDAQ Equity,OHA Investment Corporation (OHAI),OHAI
                    NASDAQ Equity,Ohio Valley Banc Corp. (OVBC),OVBC
                    NASDAQ Equity,"Ohr Pharmaceutical, Inc. (OHRP)",OHRP
                    NASDAQ Equity,"Okta, Inc. (OKTA)",OKTA
                    NASDAQ Equity,"Old Dominion Freight Line, Inc. (ODFL)",ODFL
                    NASDAQ Equity,"Old Line Bancshares, Inc. (OLBK)",OLBK
                    NASDAQ Equity,Old National Bancorp (ONB),ONB
                    NASDAQ Equity,Old Point Financial Corporation (OPOF),OPOF
                    NASDAQ Equity,"Old Second Bancorp, Inc. (OSBC)",OSBC
                    NASDAQ Equity,"Old Second Bancorp, Inc. (OSBCP)",OSBCP
                    NASDAQ Equity,"Ollie&#39;s Bargain Outlet Holdings, Inc. (OLLI)",OLLI
                    NASDAQ Equity,"Olympic Steel, Inc. (ZEUS)",ZEUS
                    NASDAQ Equity,"Omega Flex, Inc. (OFLX)",OFLX
                    NASDAQ Equity,Omeros Corporation (OMER),OMER
                    NASDAQ Equity,"Omnicell, Inc. (OMCL)",OMCL
                    NASDAQ Equity,ON Semiconductor Corporation (ON),ON
                    NASDAQ Equity,On Track Innovations Ltd (OTIV),OTIV
                    NASDAQ Equity,Oncolytics Biotech Inc. (ONCY),ONCY
                    NASDAQ Equity,"Onconova Therapeutics, Inc. (ONTX)",ONTX
                    NASDAQ Equity,"Onconova Therapeutics, Inc. (ONTXW)",ONTXW
                    NASDAQ Equity,OncoSec Medical Incorporated (ONCS),ONCS
                    NASDAQ Equity,"Oncternal Therapeutics, Inc.  (ONCT)",ONCT
                    NASDAQ Equity,"One Stop Systems, Inc. (OSS)",OSS
                    NASDAQ Equity,OneSpan Inc. (OSPN),OSPN
                    NASDAQ Equity,OneSpaWorld Holdings Limited (OSW),OSW
                    NASDAQ Equity,OP Bancorp (OPBK),OPBK
                    NASDAQ Equity,Open Text Corporation (OTEX),OTEX
                    NASDAQ Equity,Opera Limited (OPRA),OPRA
                    NASDAQ Equity,Opes Acquisition Corp. (OPES),OPES
                    NASDAQ Equity,Opes Acquisition Corp. (OPESU),OPESU
                    NASDAQ Equity,Opes Acquisition Corp. (OPESW),OPESW
                    NASDAQ Equity,"OpGen, Inc. (OPGN)",OPGN
                    NASDAQ Equity,"OpGen, Inc. (OPGNW)",OPGNW
                    NASDAQ Equity,"Opiant Pharmaceuticals, Inc. (OPNT)",OPNT
                    NASDAQ Equity,"Opko Health, Inc. (OPK)",OPK
                    NASDAQ Equity,Optibase Ltd. (OBAS),OBAS
                    NASDAQ Equity,Optical Cable Corporation (OCC),OCC
                    NASDAQ Equity,OptimizeRx Corporation (OPRX),OPRX
                    NASDAQ Equity,"OptimumBank Holdings, Inc. (OPHC)",OPHC
                    NASDAQ Equity,"OptiNose, Inc. (OPTN)",OPTN
                    NASDAQ Equity,Opus Bank (OPB),OPB
                    NASDAQ Equity,Oramed Pharmaceuticals Inc. (ORMP),ORMP
                    NASDAQ Equity,"OraSure Technologies, Inc. (OSUR)",OSUR
                    NASDAQ Equity,ORBCOMM Inc. (ORBC),ORBC
                    NASDAQ Equity,Orchard Therapeutics plc (ORTX),ORTX
                    NASDAQ Equity,"O&#39;Reilly Automotive, Inc. (ORLY)",ORLY
                    NASDAQ Equity,Organigram Holdings Inc. (OGI),OGI
                    NASDAQ Equity,Organogenesis Holdings Inc.  (ORGO),ORGO
                    NASDAQ Equity,"Organovo Holdings, Inc. (ONVO)",ONVO
                    NASDAQ Equity,Orgenesis Inc. (ORGS),ORGS
                    NASDAQ Equity,Origin Agritech Limited (SEED),SEED
                    NASDAQ Equity,"Origin Bancorp, Inc. (OBNK)",OBNK
                    NASDAQ Equity,"Orion Energy Systems, Inc. (OESX)",OESX
                    NASDAQ Equity,Oritani Financial Corp. (ORIT),ORIT
                    NASDAQ Equity,Orrstown Financial Services Inc (ORRF),ORRF
                    NASDAQ Equity,Orthofix Medical Inc.  (OFIX),OFIX
                    NASDAQ Equity,OrthoPediatrics Corp. (KIDS),KIDS
                    NASDAQ Equity,"OSI Systems, Inc. (OSIS)",OSIS
                    NASDAQ Equity,Osmotica Pharmaceuticals plc (OSMT),OSMT
                    NASDAQ Equity,"Ossen Innovation Co., Ltd. (OSN)",OSN
                    NASDAQ Equity,Otelco Inc. (OTEL),OTEL
                    NASDAQ Equity,"Otonomy, Inc. (OTIC)",OTIC
                    NASDAQ Equity,"Ottawa Bancorp, Inc. (OTTW)",OTTW
                    NASDAQ Equity,Otter Tail Corporation (OTTR),OTTR
                    NASDAQ Equity,"Outlook Therapeutics, Inc. (OTLK)",OTLK
                    NASDAQ Equity,"Outlook Therapeutics, Inc. (OTLKW)",OTLKW
                    NASDAQ Equity,"Overstock.com, Inc. (OSTK)",OSTK
                    NASDAQ Equity,Ovid Therapeutics Inc. (OVID),OVID
                    NASDAQ Equity,Oxbridge Re Holdings Limited (OXBR),OXBR
                    NASDAQ Equity,Oxbridge Re Holdings Limited (OXBRW),OXBRW
                    NASDAQ Equity,Oxford Immunotec Global PLC (OXFD),OXFD
                    NASDAQ Equity,Oxford Lane Capital Corp. (OXLC),OXLC
                    NASDAQ Equity,Oxford Lane Capital Corp. (OXLCM),OXLCM
                    NASDAQ Equity,Oxford Lane Capital Corp. (OXLCO),OXLCO
                    NASDAQ Equity,Oxford Square Capital Corp. (OXSQ),OXSQ
                    NASDAQ Equity,Oxford Square Capital Corp. (OXSQL),OXSQL
                    NASDAQ Equity,Oxford Square Capital Corp. (OXSQZ),OXSQZ
                    NASDAQ Equity,"P & F Industries, Inc. (PFIN)",PFIN
                    NASDAQ Equity,"P.A.M. Transportation Services, Inc. (PTSI)",PTSI
                    NASDAQ Equity,PACCAR Inc. (PCAR),PCAR
                    NASDAQ Equity,Pacer Cash Cows Fund of Funds ETF (HERD),HERD
                    NASDAQ Equity,Pacer Emerging Markets Cash Cows 100 ETF (ECOW),ECOW
                    NASDAQ Equity,Pacer Military Times Best Employers ETF (VETS),VETS
                    NASDAQ Equity,"Pacific Biosciences of California, Inc. (PACB)",PACB
                    NASDAQ Equity,Pacific City Financial Corporation (PCB),PCB
                    NASDAQ Equity,"Pacific Ethanol, Inc. (PEIX)",PEIX
                    NASDAQ Equity,Pacific Mercantile Bancorp (PMBC),PMBC
                    NASDAQ Equity,Pacific Premier Bancorp Inc (PPBI),PPBI
                    NASDAQ Equity,"Pacira BioSciences, Inc. (PCRX)",PCRX
                    NASDAQ Equity,PacWest Bancorp (PACW),PACW
                    NASDAQ Equity,"Palomar Holdings, Inc. (PLMR)",PLMR
                    NASDAQ Equity,Pan American Silver Corp. (PAAS),PAAS
                    NASDAQ Equity,Pangaea Logistics Solutions Ltd. (PANL),PANL
                    NASDAQ Equity,"Papa John&#39;s International, Inc. (PZZA)",PZZA
                    NASDAQ Equity,"Paratek Pharmaceuticals, Inc.  (PRTK)",PRTK
                    NASDAQ Equity,Pareteum Corporation (TEUM),TEUM
                    NASDAQ Equity,Paringa Resources Limited (PNRL),PNRL
                    NASDAQ Equity,"Park City Group, Inc. (PCYG)",PCYG
                    NASDAQ Equity,"Parke Bancorp, Inc. (PKBK)",PKBK
                    NASDAQ Equity,Park-Ohio Holdings Corp. (PKOH),PKOH
                    NASDAQ Equity,Partner Communications Company Ltd. (PTNR),PTNR
                    NASDAQ Equity,"Pathfinder Bancorp, Inc. (PBHC)",PBHC
                    NASDAQ Equity,"Patrick Industries, Inc. (PATK)",PATK
                    NASDAQ Equity,Patriot National Bancorp Inc. (PNBK),PNBK
                    NASDAQ Equity,"Patriot Transportation Holding, Inc. (PATI)",PATI
                    NASDAQ Equity,Pattern Energy Group Inc. (PEGI),PEGI
                    NASDAQ Equity,"Patterson Companies, Inc. (PDCO)",PDCO
                    NASDAQ Equity,"Patterson-UTI Energy, Inc. (PTEN)",PTEN
                    NASDAQ Equity,PAVmed Inc. (PAVM),PAVM
                    NASDAQ Equity,PAVmed Inc. (PAVMW),PAVMW
                    NASDAQ Equity,PAVmed Inc. (PAVMZ),PAVMZ
                    NASDAQ Equity,"Paychex, Inc. (PAYX)",PAYX
                    NASDAQ Equity,Paylocity Holding Corporation (PCTY),PCTY
                    NASDAQ Equity,"Payment Data Systems, Inc. (PYDS)",PYDS
                    NASDAQ Equity,"PayPal Holdings, Inc. (PYPL)",PYPL
                    NASDAQ Equity,"Paysign, Inc. (PAYS)",PAYS
                    NASDAQ Equity,"PB Bancorp, Inc. (PBBI)",PBBI
                    NASDAQ Equity,"PC Connection, Inc. (CNXN)",CNXN
                    NASDAQ Equity,"PCM, Inc. (PCMI)",PCMI
                    NASDAQ Equity,PCSB Financial Corporation (PCSB),PCSB
                    NASDAQ Equity,"PC-Tel, Inc. (PCTI)",PCTI
                    NASDAQ Equity,"PDC Energy, Inc. (PDCE)",PDCE
                    NASDAQ Equity,"PDF Solutions, Inc. (PDFS)",PDFS
                    NASDAQ Equity,"PDL BioPharma, Inc. (PDLI)",PDLI
                    NASDAQ Equity,PDL Community Bancorp (PDLB),PDLB
                    NASDAQ Equity,PDS Biotechnology Corporation (PDSB),PDSB
                    NASDAQ Equity,"pdvWireless, Inc. (ATEX)",ATEX
                    NASDAQ Equity,"Peak Resorts, Inc. (SKIS)",SKIS
                    NASDAQ Equity,Peapack-Gladstone Financial Corporation (PGC),PGC
                    NASDAQ Equity,Pegasystems Inc. (PEGA),PEGA
                    NASDAQ Equity,"Penn National Gaming, Inc. (PENN)",PENN
                    NASDAQ Equity,Penn Virginia Corporation (PVAC),PVAC
                    NASDAQ Equity,PennantPark Floating Rate Capital Ltd. (PFLT),PFLT
                    NASDAQ Equity,PennantPark Investment Corporation (PNNT),PNNT
                    NASDAQ Equity,"Penns Woods Bancorp, Inc. (PWOD)",PWOD
                    NASDAQ Equity,Pensare Acquisition Corp. (WRLS),WRLS
                    NASDAQ Equity,Pensare Acquisition Corp. (WRLSR),WRLSR
                    NASDAQ Equity,Pensare Acquisition Corp. (WRLSU),WRLSU
                    NASDAQ Equity,Pensare Acquisition Corp. (WRLSW),WRLSW
                    NASDAQ Equity,Peoples Bancorp Inc. (PEBO),PEBO
                    NASDAQ Equity,"Peoples Bancorp of North Carolina, Inc. (PEBK)",PEBK
                    NASDAQ Equity,Peoples Financial Services Corp.  (PFIS),PFIS
                    NASDAQ Equity,"People&#39;s United Financial, Inc. (PBCT)",PBCT
                    NASDAQ Equity,"People&#39;s United Financial, Inc. (PBCTP)",PBCTP
                    NASDAQ Equity,People&#39;s Utah Bancorp (PUB),PUB
                    NASDAQ Equity,"Pepper Food Service Co., Ltd. (KPFS)",KPFS
                    NASDAQ Equity,"Pepsico, Inc. (PEP)",PEP
                    NASDAQ Equity,"Perceptron, Inc. (PRCP)",PRCP
                    NASDAQ Equity,"Perficient, Inc. (PRFT)",PRFT
                    NASDAQ Equity,Performance Shipping Inc. (DCIX),DCIX
                    NASDAQ Equity,Performant Financial Corporation (PFMT),PFMT
                    NASDAQ Equity,Perion Network Ltd (PERI),PERI
                    NASDAQ Equity,"Perma-Fix Environmental Services, Inc. (PESI)",PESI
                    NASDAQ Equity,"Perma-Pipe International Holdings, Inc. (PPIH)",PPIH
                    NASDAQ Equity,"Personalis, Inc. (PSNL)",PSNL
                    NASDAQ Equity,"PetIQ, Inc. (PETQ)",PETQ
                    NASDAQ Equity,"PetMed Express, Inc. (PETS)",PETS
                    NASDAQ Equity,"PFSweb, Inc. (PFSW)",PFSW
                    NASDAQ Equity,"PGT Innovations, Inc. (PGTI)",PGTI
                    NASDAQ Equity,"PhaseBio Pharmaceuticals, Inc. (PHAS)",PHAS
                    NASDAQ Equity,Phibro Animal Health Corporation (PAHC),PAHC
                    NASDAQ Equity,Phio Pharmaceuticals Corp. (PHIO),PHIO
                    NASDAQ Equity,Phio Pharmaceuticals Corp. (PHIOW),PHIOW
                    NASDAQ Equity,"Photronics, Inc. (PLAB)",PLAB
                    NASDAQ Equity,"Phunware, Inc. (PHUN)",PHUN
                    NASDAQ Equity,"Phunware, Inc. (PHUNW)",PHUNW
                    NASDAQ Equity,PICO Holdings Inc. (PICO),PICO
                    NASDAQ Equity,Piedmont Lithium Limited (PLL),PLL
                    NASDAQ Equity,"Pieris Pharmaceuticals, Inc. (PIRS)",PIRS
                    NASDAQ Equity,Pilgrim&#39;s Pride Corporation (PPC),PPC
                    NASDAQ Equity,Pinduoduo Inc. (PDD),PDD
                    NASDAQ Equity,Pingtan Marine Enterprise Ltd. (PME),PME
                    NASDAQ Equity,"Pinnacle Financial Partners, Inc. (PNFP)",PNFP
                    NASDAQ Equity,Pintec Technology Holdings Limited (PT),PT
                    NASDAQ Equity,"Pioneer Power Solutions, Inc. (PPSI)",PPSI
                    NASDAQ Equity,"Pixelworks, Inc. (PXLW)",PXLW
                    NASDAQ Equity,Playa Hotels & Resorts N.V. (PLYA),PLYA
                    NASDAQ Equity,Plexus Corp. (PLXS),PLXS
                    NASDAQ Equity,"Plug Power, Inc. (PLUG)",PLUG
                    NASDAQ Equity,Plumas Bancorp (PLBC),PLBC
                    NASDAQ Equity,"Pluralsight, Inc. (PS)",PS
                    NASDAQ Equity,"Pluristem Therapeutics, Inc. (PSTI)",PSTI
                    NASDAQ Equity,PLx Pharma Inc. (PLXP),PLXP
                    NASDAQ Equity,Pointer Telocation Ltd. (PNTR),PNTR
                    NASDAQ Equity,"Points International, Ltd. (PCOM)",PCOM
                    NASDAQ Equity,"Polar Power, Inc. (POLA)",POLA
                    NASDAQ Equity,"PolarityTE, Inc. (PTE)",PTE
                    NASDAQ Equity,Pool Corporation (POOL),POOL
                    NASDAQ Equity,Pope Resources (POPE),POPE
                    NASDAQ Equity,"Popular, Inc. (BPOP)",BPOP
                    NASDAQ Equity,"Popular, Inc. (BPOPM)",BPOPM
                    NASDAQ Equity,"Popular, Inc. (BPOPN)",BPOPN
                    NASDAQ Equity,Portman Ridge Finance Corporation (KCAPL),KCAPL
                    NASDAQ Equity,Portman Ridge Finance Corporation (PTMN),PTMN
                    NASDAQ Equity,"Portola Pharmaceuticals, Inc. (PTLA)",PTLA
                    NASDAQ Equity,"Positive Physicians Holdings, Inc. (PPHI)",PPHI
                    NASDAQ Equity,Potbelly Corporation (PBPB),PBPB
                    NASDAQ Equity,PotlatchDeltic Corporation (PCH),PCH
                    NASDAQ Equity,"Powell Industries, Inc. (POWL)",POWL
                    NASDAQ Equity,"Power Integrations, Inc. (POWI)",POWI
                    NASDAQ Equity,"Powerbridge Technologies Co., Ltd. (PBTS)",PBTS
                    NASDAQ Equity,"PRA Group, Inc. (PRAA)",PRAA
                    NASDAQ Equity,"PRA Health Sciences, Inc. (PRAH)",PRAH
                    NASDAQ Equity,"Precipio, Inc. (PRPO)",PRPO
                    NASDAQ Equity,"Precision BioSciences, Inc. (DTIL)",DTIL
                    NASDAQ Equity,Predictive Oncology Inc. (POAI),POAI
                    NASDAQ Equity,Preferred Bank (PFBC),PFBC
                    NASDAQ Equity,Preformed Line Products Company (PLPC),PLPC
                    NASDAQ Equity,"Premier Financial Bancorp, Inc. (PFBI)",PFBI
                    NASDAQ Equity,"Premier, Inc. (PINC)",PINC
                    NASDAQ Equity,"Presidio, Inc. (PSDO)",PSDO
                    NASDAQ Equity,Prevail Therapeutics Inc. (PRVL),PRVL
                    NASDAQ Equity,"PRGX Global, Inc. (PRGX)",PRGX
                    NASDAQ Equity,"PriceSmart, Inc. (PSMT)",PSMT
                    NASDAQ Equity,PrimeEnergy Resources Corporation (PNRG),PNRG
                    NASDAQ Equity,Primo Water Corporation (PRMW),PRMW
                    NASDAQ Equity,Primoris Services Corporation (PRIM),PRIM
                    NASDAQ Equity,Principal Contrarian Value Index ETF (PVAL),PVAL
                    NASDAQ Equity,Principal Financial Group Inc (PFG),PFG
                    NASDAQ Equity,Principal Healthcare Innovators Index ETF (BTEC),BTEC
                    NASDAQ Equity,Principal Millennials Index ETF (GENY),GENY
                    NASDAQ Equity,Principal Price Setters Index ETF (PSET),PSET
                    NASDAQ Equity,Principal Shareholder Yield Index ETF (PY),PY
                    NASDAQ Equity,Principal Sustainable Momentum Index ETF (PMOM),PMOM
                    NASDAQ Equity,Principal U.S. Mega-Cap Multi-Factor Index ETF (USMC),USMC
                    NASDAQ Equity,Principal U.S. Small-Cap Multi-Factor Index ETF (PSC),PSC
                    NASDAQ Equity,Principia Biopharma Inc. (PRNB),PRNB
                    NASDAQ Equity,"Priority Technology Holdings, Inc. (PRTH)",PRTH
                    NASDAQ Equity,"Pro-Dex, Inc. (PDEX)",PDEX
                    NASDAQ Equity,"Professional Diversity Network, Inc. (IPDN)",IPDN
                    NASDAQ Equity,Proficient Alpha Acquisition Corp. (PAAC),PAAC
                    NASDAQ Equity,Proficient Alpha Acquisition Corp. (PAACR),PAACR
                    NASDAQ Equity,Proficient Alpha Acquisition Corp. (PAACU),PAACU
                    NASDAQ Equity,Proficient Alpha Acquisition Corp. (PAACW),PAACW
                    NASDAQ Equity,"Profire Energy, Inc. (PFIE)",PFIE
                    NASDAQ Equity,Progenics Pharmaceuticals Inc. (PGNX),PGNX
                    NASDAQ Equity,Progress Software Corporation (PRGS),PRGS
                    NASDAQ Equity,"Proofpoint, Inc. (PFPT)",PFPT
                    NASDAQ Equity,"ProPhase Labs, Inc. (PRPH)",PRPH
                    NASDAQ Equity,ProQR Therapeutics N.V. (PRQR),PRQR
                    NASDAQ Equity,ProShares Equities for Rising Rates ETF (EQRR),EQRR
                    NASDAQ Equity,ProShares Ultra Nasdaq Biotechnology (BIB),BIB
                    NASDAQ Equity,Proshares UltraPro Nasdaq Biotechnology (UBIO),UBIO
                    NASDAQ Equity,ProShares UltraPro QQQ (TQQQ),TQQQ
                    NASDAQ Equity,ProShares UltraPro Short NASDAQ Biotechnology (ZBIO),ZBIO
                    NASDAQ Equity,ProShares UltraPro Short QQQ (SQQQ),SQQQ
                    NASDAQ Equity,ProShares UltraShort Nasdaq Biotechnology (BIS),BIS
                    NASDAQ Equity,Prospect Capital Corporation (PSEC),PSEC
                    NASDAQ Equity,"Protagonist Therapeutics, Inc. (PTGX)",PTGX
                    NASDAQ Equity,Protective Insurance Corporation (PTVCA),PTVCA
                    NASDAQ Equity,Protective Insurance Corporation (PTVCB),PTVCB
                    NASDAQ Equity,"Proteon Therapeutics, Inc. (PRTO)",PRTO
                    NASDAQ Equity,"Proteostasis Therapeutics, Inc. (PTI)",PTI
                    NASDAQ Equity,Prothena Corporation plc (PRTA),PRTA
                    NASDAQ Equity,"Provention Bio, Inc. (PRVB)",PRVB
                    NASDAQ Equity,"Provident Bancorp, Inc. (PVBC)",PVBC
                    NASDAQ Equity,"Provident Financial Holdings, Inc. (PROV)",PROV
                    NASDAQ Equity,"Prudential Bancorp, Inc. (PBIP)",PBIP
                    NASDAQ Equity,Psychemedics Corporation (PMD),PMD
                    NASDAQ Equity,PTC Inc. (PTC),PTC
                    NASDAQ Equity,"PTC Therapeutics, Inc. (PTCT)",PTCT
                    NASDAQ Equity,"PUHUI WEALTH INVESTMENT MANAGEMENT CO., LTD. (PHCF)",PHCF
                    NASDAQ Equity,"Pulmatrix, Inc. (PULM)",PULM
                    NASDAQ Equity,"Pulse Biosciences, Inc (PLSE)",PLSE
                    NASDAQ Equity,Puma Biotechnology Inc (PBYI),PBYI
                    NASDAQ Equity,Pure Acquisition Corp. (PACQ),PACQ
                    NASDAQ Equity,Pure Acquisition Corp. (PACQU),PACQU
                    NASDAQ Equity,Pure Acquisition Corp. (PACQW),PACQW
                    NASDAQ Equity,Pure Cycle Corporation (PCYO),PCYO
                    NASDAQ Equity,"Purple Innovation, Inc. (PRPL)",PRPL
                    NASDAQ Equity,Puyi Inc. (PUYI),PUYI
                    NASDAQ Equity,Pyxis Tankers Inc. (PXS),PXS
                    NASDAQ Equity,QAD Inc. (QADA),QADA
                    NASDAQ Equity,QAD Inc. (QADB),QADB
                    NASDAQ Equity,"QCR Holdings, Inc. (QCRH)",QCRH
                    NASDAQ Equity,Qiagen N.V. (QGEN),QGEN
                    NASDAQ Equity,QIWI plc (QIWI),QIWI
                    NASDAQ Equity,"Qorvo, Inc. (QRVO)",QRVO
                    NASDAQ Equity,QUALCOMM Incorporated (QCOM),QCOM
                    NASDAQ Equity,Qualstar Corporation (QBAK),QBAK
                    NASDAQ Equity,"Qualys, Inc. (QLYS)",QLYS
                    NASDAQ Equity,Quanterix Corporation (QTRX),QTRX
                    NASDAQ Equity,Quarterhill Inc. (QTRH),QTRH
                    NASDAQ Equity,Quest Resource Holding Corporation (QRHC),QRHC
                    NASDAQ Equity,QuickLogic Corporation (QUIK),QUIK
                    NASDAQ Equity,Quidel Corporation (QDEL),QDEL
                    NASDAQ Equity,"QuinStreet, Inc. (QNST)",QNST
                    NASDAQ Equity,Qumu Corporation (QUMU),QUMU
                    NASDAQ Equity,Quotient Limited (QTNT),QTNT
                    NASDAQ Equity,"Qurate Retail, Inc. (QRTEA)",QRTEA
                    NASDAQ Equity,"Qurate Retail, Inc. (QRTEB)",QRTEB
                    NASDAQ Equity,Qutoutiao Inc. (QTT),QTT
                    NASDAQ Equity,R.R. Donnelley & Sons Company (RRD),RRD
                    NASDAQ Equity,R1 RCM Inc. (RCM),RCM
                    NASDAQ Equity,"Ra Pharmaceuticals, Inc. (RARX)",RARX
                    NASDAQ Equity,RADA Electronic Industries Ltd. (RADA),RADA
                    NASDAQ Equity,Radcom Ltd. (RDCM),RDCM
                    NASDAQ Equity,"Radius Health, Inc. (RDUS)",RDUS
                    NASDAQ Equity,"RadNet, Inc. (RDNT)",RDNT
                    NASDAQ Equity,Radware Ltd. (RDWR),RDWR
                    NASDAQ Equity,"Ramaco Resources, Inc. (METC)",METC
                    NASDAQ Equity,"Rambus, Inc. (RMBS)",RMBS
                    NASDAQ Equity,Rand Capital Corporation (RAND),RAND
                    NASDAQ Equity,"Randolph Bancorp, Inc. (RNDB)",RNDB
                    NASDAQ Equity,"Rapid7, Inc. (RPD)",RPD
                    NASDAQ Equity,Rattler Midstream LP (RTLR),RTLR
                    NASDAQ Equity,"Rave Restaurant Group, Inc. (RAVE)",RAVE
                    NASDAQ Equity,"Raven Industries, Inc. (RAVN)",RAVN
                    NASDAQ Equity,RBB Bancorp (RBB),RBB
                    NASDAQ Equity,RBC Bearings Incorporated (ROLL),ROLL
                    NASDAQ Equity,"RCI Hospitality Holdings, Inc. (RICK)",RICK
                    NASDAQ Equity,"RCM Technologies, Inc. (RCMT)",RCMT
                    NASDAQ Equity,Reading International Inc (RDI),RDI
                    NASDAQ Equity,Reading International Inc (RDIB),RDIB
                    NASDAQ Equity,Reality Shares Nasdaq NexGen Economy China ETF (BCNA),BCNA
                    NASDAQ Equity,Reality Shares Nasdaq NextGen Economy ETF (BLCN),BLCN
                    NASDAQ Equity,Realm Therapeutics plc (RLM),RLM
                    NASDAQ Equity,"RealNetworks, Inc. (RNWK)",RNWK
                    NASDAQ Equity,"RealPage, Inc. (RP)",RP
                    NASDAQ Equity,"Reata Pharmaceuticals, Inc. (RETA)",RETA
                    NASDAQ Equity,"Recon Technology, Ltd. (RCON)",RCON
                    NASDAQ Equity,"Recro Pharma, Inc. (REPH)",REPH
                    NASDAQ Equity,"Red River Bancshares, Inc. (RRBI)",RRBI
                    NASDAQ Equity,"Red Robin Gourmet Burgers, Inc. (RRGB)",RRGB
                    NASDAQ Equity,"Red Rock Resorts, Inc. (RRR)",RRR
                    NASDAQ Equity,"Red Violet, Inc. (RDVT)",RDVT
                    NASDAQ Equity,Redfin Corporation (RDFN),RDFN
                    NASDAQ Equity,Redhill Biopharma Ltd. (RDHL),RDHL
                    NASDAQ Equity,Reebonz Holding Limited (RBZ),RBZ
                    NASDAQ Equity,"Reeds, Inc. (REED)",REED
                    NASDAQ Equity,Regency Centers Corporation (REG),REG
                    NASDAQ Equity,"Regeneron Pharmaceuticals, Inc. (REGN)",REGN
                    NASDAQ Equity,REGENXBIO Inc. (RGNX),RGNX
                    NASDAQ Equity,Regulus Therapeutics Inc. (RGLS),RGLS
                    NASDAQ Equity,"Rekor Systems, Inc. (REKR)",REKR
                    NASDAQ Equity,"Reliant Bancorp, Inc. (RBNC)",RBNC
                    NASDAQ Equity,"Reliv&#39; International, Inc. (RELV)",RELV
                    NASDAQ Equity,"Remark Holdings, Inc. (MARK)",MARK
                    NASDAQ Equity,Renasant Corporation (RNST),RNST
                    NASDAQ Equity,"Renewable Energy Group, Inc. (REGI)",REGI
                    NASDAQ Equity,Rent-A-Center Inc. (RCII),RCII
                    NASDAQ Equity,Repligen Corporation (RGEN),RGEN
                    NASDAQ Equity,"Replimune Group, Inc. (REPL)",REPL
                    NASDAQ Equity,"Republic Bancorp, Inc. (RBCAA)",RBCAA
                    NASDAQ Equity,"Republic First Bancorp, Inc. (FRBK)",FRBK
                    NASDAQ Equity,Research Frontiers Incorporated (REFR),REFR
                    NASDAQ Equity,Resonant Inc. (RESN),RESN
                    NASDAQ Equity,"Resources Connection, Inc. (RECN)",RECN
                    NASDAQ Equity,"Restoration Robotics, Inc. (HAIR)",HAIR
                    NASDAQ Equity,"resTORbio, Inc. (TORC)",TORC
                    NASDAQ Equity,Retail Opportunity Investments Corp. (ROIC),ROIC
                    NASDAQ Equity,"ReTo Eco-Solutions, Inc. (RETO)",RETO
                    NASDAQ Equity,"Retrophin, Inc. (RTRX)",RTRX
                    NASDAQ Equity,"Revance Therapeutics, Inc. (RVNC)",RVNC
                    NASDAQ Equity,"Reven Housing REIT, Inc. (RVEN)",RVEN
                    NASDAQ Equity,"Revolution Lighting Technologies, Inc. (RVLT)",RVLT
                    NASDAQ Equity,ReWalk Robotics Ltd. (RWLK),RWLK
                    NASDAQ Equity,"Rexahn Pharmaceuticals, Inc. (REXN)",REXN
                    NASDAQ Equity,"RF Industries, Ltd. (RFIL)",RFIL
                    NASDAQ Equity,RGC Resources Inc. (RGCO),RGCO
                    NASDAQ Equity,"Rhinebeck Bancorp, Inc. (RBKB)",RBKB
                    NASDAQ Equity,"Rhythm Pharmaceuticals, Inc. (RYTM)",RYTM
                    NASDAQ Equity,Ribbon Communications Inc.  (RBBN),RBBN
                    NASDAQ Equity,RiceBran Technologies (RIBT),RIBT
                    NASDAQ Equity,"Richardson Electronics, Ltd. (RELL)",RELL
                    NASDAQ Equity,"Rigel Pharmaceuticals, Inc. (RIGL)",RIGL
                    NASDAQ Equity,"RigNet, Inc. (RNET)",RNET
                    NASDAQ Equity,"Rimini Street, Inc. (RMNI)",RMNI
                    NASDAQ Equity,"Riot Blockchain, Inc (RIOT)",RIOT
                    NASDAQ Equity,RISE Education Cayman Ltd (REDU),REDU
                    NASDAQ Equity,"Ritter Pharmaceuticals, Inc. (RTTR)",RTTR
                    NASDAQ Equity,Riverview Bancorp Inc (RVSB),RVSB
                    NASDAQ Equity,Riverview Financial Corporation (RIVE),RIVE
                    NASDAQ Equity,"Rocket Pharmaceuticals, Inc. (RCKT)",RCKT
                    NASDAQ Equity,"Rockwell Medical, Inc. (RMTI)",RMTI
                    NASDAQ Equity,"Rocky Brands, Inc. (RCKY)",RCKY
                    NASDAQ Equity,"Rocky Mountain Chocolate Factory, Inc. (RMCF)",RMCF
                    NASDAQ Equity,"Roku, Inc. (ROKU)",ROKU
                    NASDAQ Equity,Rosehill Resources Inc. (ROSE),ROSE
                    NASDAQ Equity,Rosehill Resources Inc. (ROSEU),ROSEU
                    NASDAQ Equity,Rosehill Resources Inc. (ROSEW),ROSEW
                    NASDAQ Equity,"Ross Stores, Inc. (ROST)",ROST
                    NASDAQ Equity,"Royal Gold, Inc. (RGLD)",RGLD
                    NASDAQ Equity,"RTI Surgical Holdings, Inc. (RTIX)",RTIX
                    NASDAQ Equity,"Rubicon Technology, Inc. (RBCN)",RBCN
                    NASDAQ Equity,"Rubius Therapeutics, Inc. (RUBY)",RUBY
                    NASDAQ Equity,Ruhnn Holding Limited (RUHN),RUHN
                    NASDAQ Equity,"RumbleOn, Inc. (RMBL)",RMBL
                    NASDAQ Equity,"Rush Enterprises, Inc. (RUSHA)",RUSHA
                    NASDAQ Equity,"Rush Enterprises, Inc. (RUSHB)",RUSHB
                    NASDAQ Equity,"Ruth&#39;s Hospitality Group, Inc. (RUTH)",RUTH
                    NASDAQ Equity,Ryanair Holdings plc (RYAAY),RYAAY
                    NASDAQ Equity,"S&T Bancorp, Inc. (STBA)",STBA
                    NASDAQ Equity,S&W Seed Company (SANW),SANW
                    NASDAQ Equity,"Sabra Health Care REIT, Inc. (SBRA)",SBRA
                    NASDAQ Equity,Sabre Corporation (SABR),SABR
                    NASDAQ Equity,"SAExploration Holdings, Inc. (SAEX)",SAEX
                    NASDAQ Equity,Safe-T Group Ltd. (SFET),SFET
                    NASDAQ Equity,"Safety Insurance Group, Inc. (SAFT)",SAFT
                    NASDAQ Equity,"Saga Communications, Inc. (SGA)",SGA
                    NASDAQ Equity,"Sage Therapeutics, Inc. (SAGE)",SAGE
                    NASDAQ Equity,"Saia, Inc. (SAIA)",SAIA
                    NASDAQ Equity,"Salem Media Group, Inc. (SALM)",SALM
                    NASDAQ Equity,"Salisbury Bancorp, Inc. (SAL)",SAL
                    NASDAQ Equity,"Sanderson Farms, Inc. (SAFM)",SAFM
                    NASDAQ Equity,"Sandy Spring Bancorp, Inc. (SASR)",SASR
                    NASDAQ Equity,"Sangamo Therapeutics, Inc. (SGMO)",SGMO
                    NASDAQ Equity,Sanmina Corporation (SANM),SANM
                    NASDAQ Equity,Sanofi (GCVRZ),GCVRZ
                    NASDAQ Equity,Sanofi (SNY),SNY
                    NASDAQ Equity,Sapiens International Corporation N.V. (SPNS),SPNS
                    NASDAQ Equity,"Sarepta Therapeutics, Inc. (SRPT)",SRPT
                    NASDAQ Equity,"Savara, Inc. (SVRA)",SVRA
                    NASDAQ Equity,"SB Financial Group, Inc. (SBFG)",SBFG
                    NASDAQ Equity,"SB Financial Group, Inc. (SBFGP)",SBFGP
                    NASDAQ Equity,SB One Bancorp (SBBX),SBBX
                    NASDAQ Equity,SBA Communications Corporation (SBAC),SBAC
                    NASDAQ Equity,"ScanSource, Inc. (SCSC)",SCSC
                    NASDAQ Equity,"Schmitt Industries, Inc. (SMIT)",SMIT
                    NASDAQ Equity,"Schnitzer Steel Industries, Inc. (SCHN)",SCHN
                    NASDAQ Equity,Scholar Rock Holding Corporation (SRRK),SRRK
                    NASDAQ Equity,Scholastic Corporation (SCHL),SCHL
                    NASDAQ Equity,Schultze Special Purpose Acquisition Corp. (SAMA),SAMA
                    NASDAQ Equity,Schultze Special Purpose Acquisition Corp. (SAMAU),SAMAU
                    NASDAQ Equity,Schultze Special Purpose Acquisition Corp. (SAMAW),SAMAW
                    NASDAQ Equity,Scientific Games Corp (SGMS),SGMS
                    NASDAQ Equity,SciPlay Corporation (SCPL),SCPL
                    NASDAQ Equity,scPharmaceuticals Inc. (SCPH),SCPH
                    NASDAQ Equity,SCWorx Corp. (WORX),WORX
                    NASDAQ Equity,"SCYNEXIS, Inc. (SCYX)",SCYX
                    NASDAQ Equity,"SeaChange International, Inc. (SEAC)",SEAC
                    NASDAQ Equity,Seacoast Banking Corporation of Florida (SBCF),SBCF
                    NASDAQ Equity,Seagate Technology PLC (STX),STX
                    NASDAQ Equity,Seanergy Maritime Holdings Corp (SHIP),SHIP
                    NASDAQ Equity,Seanergy Maritime Holdings Corp (SHIPW),SHIPW
                    NASDAQ Equity,Seanergy Maritime Holdings Corp (SHIPZ),SHIPZ
                    NASDAQ Equity,"Sears Hometown and Outlet Stores, Inc. (SHOS)",SHOS
                    NASDAQ Equity,SeaSpine Holdings Corporation (SPNE),SPNE
                    NASDAQ Equity,"Seattle Genetics, Inc. (SGEN)",SGEN
                    NASDAQ Equity,"Second Sight Medical Products, Inc. (EYES)",EYES
                    NASDAQ Equity,"Second Sight Medical Products, Inc. (EYESW)",EYESW
                    NASDAQ Equity,Secoo Holding Limited (SECO),SECO
                    NASDAQ Equity,SecureWorks Corp. (SCWX),SCWX
                    NASDAQ Equity,Security National Financial Corporation (SNFCA),SNFCA
                    NASDAQ Equity,"Seelos Therapeutics, Inc. (SEEL)",SEEL
                    NASDAQ Equity,SEI Investments Company (SEIC),SEIC
                    NASDAQ Equity,"Select Bancorp, Inc. (SLCT)",SLCT
                    NASDAQ Equity,"Select Interior Concepts, Inc. (SIC)",SIC
                    NASDAQ Equity,"Selecta Biosciences, Inc. (SELB)",SELB
                    NASDAQ Equity,"Selective Insurance Group, Inc. (SIGI)",SIGI
                    NASDAQ Equity,"SELLAS Life Sciences Group, Inc.  (SLS)",SLS
                    NASDAQ Equity,SemiLEDS Corporation (LEDS),LEDS
                    NASDAQ Equity,Semtech Corporation (SMTC),SMTC
                    NASDAQ Equity,Seneca Foods Corp. (SENEA),SENEA
                    NASDAQ Equity,Seneca Foods Corp. (SENEB),SENEB
                    NASDAQ Equity,"SenesTech, Inc. (SNES)",SNES
                    NASDAQ Equity,Senior Housing Properties Trust (SNH),SNH
                    NASDAQ Equity,Senior Housing Properties Trust (SNHNI),SNHNI
                    NASDAQ Equity,Senior Housing Properties Trust (SNHNL),SNHNL
                    NASDAQ Equity,Senmiao Technology Limited (AIHS),AIHS
                    NASDAQ Equity,"Sensus Healthcare, Inc. (SRTS)",SRTS
                    NASDAQ Equity,"Sensus Healthcare, Inc. (SRTSW)",SRTSW
                    NASDAQ Equity,Sentinel Energy Services Inc. (STNL),STNL
                    NASDAQ Equity,Sentinel Energy Services Inc. (STNLU),STNLU
                    NASDAQ Equity,Sentinel Energy Services Inc. (STNLW),STNLW
                    NASDAQ Equity,"Sequential Brands Group, Inc. (SQBG)",SQBG
                    NASDAQ Equity,"Seres Therapeutics, Inc. (MCRB)",MCRB
                    NASDAQ Equity,"ServiceSource International, Inc. (SREV)",SREV
                    NASDAQ Equity,"ServisFirst Bancshares, Inc. (SFBS)",SFBS
                    NASDAQ Equity,"Sesen Bio, Inc. (SESN)",SESN
                    NASDAQ Equity,Severn Bancorp Inc (SVBI),SVBI
                    NASDAQ Equity,"SG Blocks, Inc. (SGBX)",SGBX
                    NASDAQ Equity,"SGOCO Group, Ltd (SGOC)",SGOC
                    NASDAQ Equity,Sharps Compliance Corp. (SMED),SMED
                    NASDAQ Equity,"SharpSpring, Inc. (SHSP)",SHSP
                    NASDAQ Equity,Shenandoah Telecommunications Co (SHEN),SHEN
                    NASDAQ Equity,"ShiftPixy, Inc. (PIXY)",PIXY
                    NASDAQ Equity,"Shiloh Industries, Inc. (SHLO)",SHLO
                    NASDAQ Equity,"Shineco, Inc. (TYHT)",TYHT
                    NASDAQ Equity,"ShockWave Medical, Inc. (SWAV)",SWAV
                    NASDAQ Equity,"Shoe Carnival, Inc. (SCVL)",SCVL
                    NASDAQ Equity,Shore Bancshares Inc (SHBI),SHBI
                    NASDAQ Equity,"ShotSpotter, Inc. (SSTI)",SSTI
                    NASDAQ Equity,"Shutterfly, Inc. (SFLY)",SFLY
                    NASDAQ Equity,"SI-BONE, Inc. (SIBN)",SIBN
                    NASDAQ Equity,Siebert Financial Corp. (SIEB),SIEB
                    NASDAQ Equity,"Sienna Biopharmaceuticals, Inc. (SNNA)",SNNA
                    NASDAQ Equity,"Sientra, Inc. (SIEN)",SIEN
                    NASDAQ Equity,Sierra Bancorp (BSRR),BSRR
                    NASDAQ Equity,"Sierra Oncology, Inc. (SRRA)",SRRA
                    NASDAQ Equity,"Sierra Wireless, Inc. (SWIR)",SWIR
                    NASDAQ Equity,Sify Technologies Limited (SIFY),SIFY
                    NASDAQ Equity,SIGA Technologies Inc. (SIGA),SIGA
                    NASDAQ Equity,"Sigma Labs, Inc. (SGLB)",SGLB
                    NASDAQ Equity,"Sigma Labs, Inc. (SGLBW)",SGLBW
                    NASDAQ Equity,"SigmaTron International, Inc. (SGMA)",SGMA
                    NASDAQ Equity,Signature Bank (SBNY),SBNY
                    NASDAQ Equity,Silgan Holdings Inc. (SLGN),SLGN
                    NASDAQ Equity,Silicom Ltd (SILC),SILC
                    NASDAQ Equity,"Silicon Laboratories, Inc. (SLAB)",SLAB
                    NASDAQ Equity,Silicon Motion Technology Corporation (SIMO),SIMO
                    NASDAQ Equity,"Silk Road Medical, Inc. (SILK)",SILK
                    NASDAQ Equity,Silvercrest Asset Management Group Inc. (SAMG),SAMG
                    NASDAQ Equity,"SilverSun Technologies, Inc. (SSNT)",SSNT
                    NASDAQ Equity,Simmons First National Corporation (SFNC),SFNC
                    NASDAQ Equity,"Simulations Plus, Inc. (SLP)",SLP
                    NASDAQ Equity,Sina Corporation (SINA),SINA
                    NASDAQ Equity,"Sinclair Broadcast Group, Inc. (SBGI)",SBGI
                    NASDAQ Equity,"Sino-Global Shipping America, Ltd. (SINO)",SINO
                    NASDAQ Equity,"Sinovac Biotech, Ltd. (SVA)",SVA
                    NASDAQ Equity,"SiNtx Technologies, Inc. (SINT)",SINT
                    NASDAQ Equity,"Sirius International Insurance Group, Ltd. (SG)",SG
                    NASDAQ Equity,Sirius XM Holdings Inc. (SIRI),SIRI
                    NASDAQ Equity,"SITO Mobile, Ltd. (SITO)",SITO
                    NASDAQ Equity,"Sky Solar Holdings, Ltd. (SKYS)",SKYS
                    NASDAQ Equity,"SkyWest, Inc. (SKYW)",SKYW
                    NASDAQ Equity,"Skyworks Solutions, Inc. (SWKS)",SWKS
                    NASDAQ Equity,Sleep Number Corporation (SNBR),SNBR
                    NASDAQ Equity,SLM Corporation (SLM),SLM
                    NASDAQ Equity,SLM Corporation (SLMBP),SLMBP
                    NASDAQ Equity,"SMART Global Holdings, Inc. (SGH)",SGH
                    NASDAQ Equity,"Smart Sand, Inc. (SND)",SND
                    NASDAQ Equity,"SmartFinancial, Inc. (SMBK)",SMBK
                    NASDAQ Equity,"Smith Micro Software, Inc. (SMSI)",SMSI
                    NASDAQ Equity,SMTC Corporation (SMTX),SMTX
                    NASDAQ Equity,"Social Reality, Inc. (SRAX)",SRAX
                    NASDAQ Equity,"Socket Mobile, Inc. (SCKT)",SCKT
                    NASDAQ Equity,SoFi Gig Economy ETF (GIGE),GIGE
                    NASDAQ Equity,Sohu.com Limited  (SOHU),SOHU
                    NASDAQ Equity,Solar Capital Ltd. (SLRC),SLRC
                    NASDAQ Equity,Solar Senior Capital Ltd. (SUNS),SUNS
                    NASDAQ Equity,"SolarEdge Technologies, Inc. (SEDG)",SEDG
                    NASDAQ Equity,"Soleno Therapeutics, Inc. (SLNO)",SLNO
                    NASDAQ Equity,"Soleno Therapeutics, Inc. (SLNOW)",SLNOW
                    NASDAQ Equity,Sol-Gel Technologies Ltd. (SLGL),SLGL
                    NASDAQ Equity,Solid Biosciences Inc. (SLDB),SLDB
                    NASDAQ Equity,"Soligenix, Inc. (SNGX)",SNGX
                    NASDAQ Equity,"Soligenix, Inc. (SNGXW)",SNGXW
                    NASDAQ Equity,"Soliton, Inc. (SOLY)",SOLY
                    NASDAQ Equity,"Sonim Technologies, Inc. (SONM)",SONM
                    NASDAQ Equity,"Sonoma Pharmaceuticals, Inc. (SNOA)",SNOA
                    NASDAQ Equity,"Sonoma Pharmaceuticals, Inc. (SNOAW)",SNOAW
                    NASDAQ Equity,"Sonos, Inc. (SONO)",SONO
                    NASDAQ Equity,"Sophiris Bio, Inc. (SPHS)",SPHS
                    NASDAQ Equity,"SORL Auto Parts, Inc. (SORL)",SORL
                    NASDAQ Equity,"Sorrento Therapeutics, Inc. (SRNE)",SRNE
                    NASDAQ Equity,Sotherly Hotels Inc. (SOHO),SOHO
                    NASDAQ Equity,Sotherly Hotels Inc. (SOHOB),SOHOB
                    NASDAQ Equity,Sotherly Hotels Inc. (SOHON),SOHON
                    NASDAQ Equity,Sotherly Hotels Inc. (SOHOO),SOHOO
                    NASDAQ Equity,"Sound Financial Bancorp, Inc. (SFBC)",SFBC
                    NASDAQ Equity,South Mountain Merger Corp. (SMMCU),SMMCU
                    NASDAQ Equity,"South Plains Financial, Inc. (SPFI)",SPFI
                    NASDAQ Equity,South State Corporation (SSB),SSB
                    NASDAQ Equity,"Southern First Bancshares, Inc. (SFST)",SFST
                    NASDAQ Equity,"Southern Missouri Bancorp, Inc. (SMBC)",SMBC
                    NASDAQ Equity,"Southern National Bancorp of Virginia, Inc. (SONA)",SONA
                    NASDAQ Equity,"Southside Bancshares, Inc. (SBSI)",SBSI
                    NASDAQ Equity,So-Young International Inc. (SY),SY
                    NASDAQ Equity,SP Plus Corporation (SP),SP
                    NASDAQ Equity,"SPAR Group, Inc. (SGRP)",SGRP
                    NASDAQ Equity,"Spark Energy, Inc. (SPKE)",SPKE
                    NASDAQ Equity,"Spark Energy, Inc. (SPKEP)",SPKEP
                    NASDAQ Equity,"Spark Therapeutics, Inc. (ONCE)",ONCE
                    NASDAQ Equity,"Spartan Motors, Inc. (SPAR)",SPAR
                    NASDAQ Equity,SpartanNash Company (SPTN),SPTN
                    NASDAQ Equity,SPDR Dorsey Wright Fixed Income Allocation ETF (DWFI),DWFI
                    NASDAQ Equity,"Spectrum Pharmaceuticals, Inc. (SPPI)",SPPI
                    NASDAQ Equity,"Spero Therapeutics, Inc. (SPRO)",SPRO
                    NASDAQ Equity,Sphere 3D Corp. (ANY),ANY
                    NASDAQ Equity,Spherix Incorporated (SPEX),SPEX
                    NASDAQ Equity,"SPI Energy Co., Ltd. (SPI)",SPI
                    NASDAQ Equity,"Spirit Airlines, Inc. (SAVE)",SAVE
                    NASDAQ Equity,"Spirit of Texas Bancshares, Inc. (STXB)",STXB
                    NASDAQ Equity,Splunk Inc. (SPLK),SPLK
                    NASDAQ Equity,"Spok Holdings, Inc. (SPOK)",SPOK
                    NASDAQ Equity,"Sportsman&#39;s Warehouse Holdings, Inc. (SPWH)",SPWH
                    NASDAQ Equity,"Spring Bank Pharmaceuticals, Inc. (SBPH)",SBPH
                    NASDAQ Equity,"Sprott Focus Trust, Inc. (FUND)",FUND
                    NASDAQ Equity,"Sprouts Farmers Market, Inc. (SFM)",SFM
                    NASDAQ Equity,"SPS Commerce, Inc. (SPSC)",SPSC
                    NASDAQ Equity,"SS&C Technologies Holdings, Inc. (SSNC)",SSNC
                    NASDAQ Equity,SSLJ.com Limited (YGTY),YGTY
                    NASDAQ Equity,SSR Mining Inc. (SSRM),SSRM
                    NASDAQ Equity,STAAR Surgical Company (STAA),STAA
                    NASDAQ Equity,"Staffing 360 Solutions, Inc. (STAF)",STAF
                    NASDAQ Equity,Stamps.com Inc. (STMP),STMP
                    NASDAQ Equity,Standard AVB Financial Corp. (STND),STND
                    NASDAQ Equity,Star Bulk Carriers Corp. (SBLK),SBLK
                    NASDAQ Equity,Star Bulk Carriers Corp. (SBLKZ),SBLKZ
                    NASDAQ Equity,Starbucks Corporation (SBUX),SBUX
                    NASDAQ Equity,State Auto Financial Corporation (STFC),STFC
                    NASDAQ Equity,Stealth BioTherapeutics Corp. (MITO),MITO
                    NASDAQ Equity,"StealthGas, Inc. (GASS)",GASS
                    NASDAQ Equity,"Steel Connect, Inc. (STCN)",STCN
                    NASDAQ Equity,"Steel Dynamics, Inc. (STLD)",STLD
                    NASDAQ Equity,"Stein Mart, Inc. (SMRT)",SMRT
                    NASDAQ Equity,"Stemline Therapeutics, Inc. (STML)",STML
                    NASDAQ Equity,"Stericycle, Inc. (SRCL)",SRCL
                    NASDAQ Equity,"Sterling Bancorp, Inc. (SBT)",SBT
                    NASDAQ Equity,Sterling Construction Company Inc (STRL),STRL
                    NASDAQ Equity,"Steven Madden, Ltd. (SHOO)",SHOO
                    NASDAQ Equity,Stewardship Financial Corp (SSFN),SSFN
                    NASDAQ Equity,"Stitch Fix, Inc. (SFIX)",SFIX
                    NASDAQ Equity,"Stock Yards Bancorp, Inc. (SYBT)",SYBT
                    NASDAQ Equity,"Stoke Therapeutics, Inc. (STOK)",STOK
                    NASDAQ Equity,StoneCastle Financial Corp (BANX),BANX
                    NASDAQ Equity,StoneCo Ltd. (STNE),STNE
                    NASDAQ Equity,"Strata Skin Sciences, Inc. (SSKN)",SSKN
                    NASDAQ Equity,"Stratasys, Ltd. (SSYS)",SSYS
                    NASDAQ Equity,"Strategic Education, Inc. (STRA)",STRA
                    NASDAQ Equity,Strategy Shares Nasdaq 7HANDL Index ETF (HNDL),HNDL
                    NASDAQ Equity,Strattec Security Corporation (STRT),STRT
                    NASDAQ Equity,Stratus Properties Inc. (STRS),STRS
                    NASDAQ Equity,"Streamline Health Solutions, Inc. (STRM)",STRM
                    NASDAQ Equity,Strongbridge Biopharma plc (SBBP),SBBP
                    NASDAQ Equity,"Summer Infant, Inc. (SUMR)",SUMR
                    NASDAQ Equity,"Summit Financial Group, Inc. (SMMF)",SMMF
                    NASDAQ Equity,Summit State Bank (SSBI),SSBI
                    NASDAQ Equity,Summit Therapeutics plc (SMMT),SMMT
                    NASDAQ Equity,"Summit Wireless Technologies, Inc. (WISA)",WISA
                    NASDAQ Equity,Sundance Energy Australia Limited (SNDE),SNDE
                    NASDAQ Equity,"Sunesis Pharmaceuticals, Inc. (SNSS)",SNSS
                    NASDAQ Equity,"SunOpta, Inc. (STKL)",STKL
                    NASDAQ Equity,SunPower Corporation (SPWR),SPWR
                    NASDAQ Equity,Sunrun Inc. (RUN),RUN
                    NASDAQ Equity,"Sunworks, Inc. (SUNW)",SUNW
                    NASDAQ Equity,"Super League Gaming, Inc. (SLGG)",SLGG
                    NASDAQ Equity,"SuperCom, Ltd. (SPCB)",SPCB
                    NASDAQ Equity,Superconductor Technologies Inc. (SCON),SCON
                    NASDAQ Equity,"Superior Group of Companies, Inc. (SGC)",SGC
                    NASDAQ Equity,"Supernus Pharmaceuticals, Inc. (SUPN)",SUPN
                    NASDAQ Equity,"support.com, Inc. (SPRT)",SPRT
                    NASDAQ Equity,"Surface Oncology, Inc. (SURF)",SURF
                    NASDAQ Equity,"Surgery Partners, Inc. (SGRY)",SGRY
                    NASDAQ Equity,"Surmodics, Inc. (SRDX)",SRDX
                    NASDAQ Equity,"Sutro Biopharma, Inc. (STRO)",STRO
                    NASDAQ Equity,SVB Financial Group (SIVB),SIVB
                    NASDAQ Equity,SVMK Inc. (SVMK),SVMK
                    NASDAQ Equity,"Sykes Enterprises, Incorporated (SYKE)",SYKE
                    NASDAQ Equity,Symantec Corporation (SYMC),SYMC
                    NASDAQ Equity,"Synacor, Inc. (SYNC)",SYNC
                    NASDAQ Equity,Synalloy Corporation (SYNL),SYNL
                    NASDAQ Equity,Synaptics Incorporated (SYNA),SYNA
                    NASDAQ Equity,"Synchronoss Technologies, Inc. (SNCR)",SNCR
                    NASDAQ Equity,"Syndax Pharmaceuticals, Inc. (SNDX)",SNDX
                    NASDAQ Equity,"Syneos Health, Inc. (SYNH)",SYNH
                    NASDAQ Equity,"Synlogic, Inc. (SYBX)",SYBX
                    NASDAQ Equity,"Synopsys, Inc. (SNPS)",SNPS
                    NASDAQ Equity,"Synthesis Energy Systems, Inc. (SES)",SES
                    NASDAQ Equity,"Synthorx, Inc. (THOR)",THOR
                    NASDAQ Equity,"Sypris Solutions, Inc. (SYPR)",SYPR
                    NASDAQ Equity,"Syros Pharmaceuticals, Inc. (SYRS)",SYRS
                    NASDAQ Equity,"T. Rowe Price Group, Inc. (TROW)",TROW
                    NASDAQ Equity,"T2 Biosystems, Inc. (TTOO)",TTOO
                    NASDAQ Equity,"Tabula Rasa HealthCare, Inc. (TRHC)",TRHC
                    NASDAQ Equity,"Tactile Systems Technology, Inc. (TCMD)",TCMD
                    NASDAQ Equity,Taitron Components Incorporated (TAIT),TAIT
                    NASDAQ Equity,"Taiwan Liposome Company, Ltd. (TLC)",TLC
                    NASDAQ Equity,"Take-Two Interactive Software, Inc. (TTWO)",TTWO
                    NASDAQ Equity,Talend S.A. (TLND),TLND
                    NASDAQ Equity,"Tandem Diabetes Care, Inc. (TNDM)",TNDM
                    NASDAQ Equity,"Tandy Leather Factory, Inc. (TLF)",TLF
                    NASDAQ Equity,Tantech Holdings Ltd. (TANH),TANH
                    NASDAQ Equity,Taoping Inc. (TAOP),TAOP
                    NASDAQ Equity,"Tarena International, Inc. (TEDU)",TEDU
                    NASDAQ Equity,Target Hospitality Corp. (TH),TH
                    NASDAQ Equity,Target Hospitality Corp. (THWWW),THWWW
                    NASDAQ Equity,"Taronis Technologies, Inc. (TRNX)",TRNX
                    NASDAQ Equity,TAT Technologies Ltd. (TATT),TATT
                    NASDAQ Equity,"Taylor Devices, Inc. (TAYD)",TAYD
                    NASDAQ Equity,"TCG BDC, Inc. (CGBD)",CGBD
                    NASDAQ Equity,TCR2 Therapeutics Inc. (TCRR),TCRR
                    NASDAQ Equity,TD Ameritrade Holding Corporation (AMTD),AMTD
                    NASDAQ Equity,"TDH Holdings, Inc. (PETZ)",PETZ
                    NASDAQ Equity,Tech Data Corporation (TECD),TECD
                    NASDAQ Equity,Technical Communications Corporation (TCCO),TCCO
                    NASDAQ Equity,"TechTarget, Inc. (TTGT)",TTGT
                    NASDAQ Equity,Tecnoglass Inc. (TGLS),TGLS
                    NASDAQ Equity,Tecogen Inc. (TGEN),TGEN
                    NASDAQ Equity,"Tectonic Financial, Inc. (TECTP)",TECTP
                    NASDAQ Equity,"Telenav, Inc. (TNAV)",TNAV
                    NASDAQ Equity,"Teligent, Inc. (TLGT)",TLGT
                    NASDAQ Equity,Tellurian Inc. (TELL),TELL
                    NASDAQ Equity,"Tenable Holdings, Inc. (TENB)",TENB
                    NASDAQ Equity,"Tenax Therapeutics, Inc. (TENX)",TENX
                    NASDAQ Equity,Tenzing Acquisition Corp. (TZAC),TZAC
                    NASDAQ Equity,Tenzing Acquisition Corp. (TZACU),TZACU
                    NASDAQ Equity,Tenzing Acquisition Corp. (TZACW),TZACW
                    NASDAQ Equity,"Teradyne, Inc. (TER)",TER
                    NASDAQ Equity,"TerraForm Power, Inc. (TERP)",TERP
                    NASDAQ Equity,Territorial Bancorp Inc. (TBNK),TBNK
                    NASDAQ Equity,"Tesla, Inc.  (TSLA)",TSLA
                    NASDAQ Equity,TESSCO Technologies Incorporated (TESS),TESS
                    NASDAQ Equity,"Tetra Tech, Inc. (TTEK)",TTEK
                    NASDAQ Equity,"Tetraphase Pharmaceuticals, Inc. (TTPH)",TTPH
                    NASDAQ Equity,"Texas Capital Bancshares, Inc. (TCBI)",TCBI
                    NASDAQ Equity,"Texas Capital Bancshares, Inc. (TCBIL)",TCBIL
                    NASDAQ Equity,"Texas Capital Bancshares, Inc. (TCBIP)",TCBIP
                    NASDAQ Equity,Texas Instruments Incorporated (TXN),TXN
                    NASDAQ Equity,"Texas Roadhouse, Inc. (TXRH)",TXRH
                    NASDAQ Equity,TFS Financial Corporation (TFSL),TFSL
                    NASDAQ Equity,"TG Therapeutics, Inc. (TGTX)",TGTX
                    NASDAQ Equity,The Alkaline Water Company Inc. (WTER),WTER
                    NASDAQ Equity,"The Andersons, Inc. (ANDE)",ANDE
                    NASDAQ Equity,"The Bancorp, Inc. (TBBK)",TBBK
                    NASDAQ Equity,The Bank of Princeton (BPRN),BPRN
                    NASDAQ Equity,The Carlyle Group L.P. (CG),CG
                    NASDAQ Equity,The Carlyle Group L.P. (TCGP),TCGP
                    NASDAQ Equity,The Cheesecake Factory Incorporated (CAKE),CAKE
                    NASDAQ Equity,"The Chefs&#39; Warehouse, Inc. (CHEF)",CHEF
                    NASDAQ Equity,The Community Financial Corporation (TCFC),TCFC
                    NASDAQ Equity,The Descartes Systems Group Inc. (DSGX),DSGX
                    NASDAQ Equity,"The Dixie Group, Inc. (DXYN)",DXYN
                    NASDAQ Equity,"The Ensign Group, Inc. (ENSG)",ENSG
                    NASDAQ Equity,The ExOne Company (XONE),XONE
                    NASDAQ Equity,"The First Bancshares, Inc. (FBMS)",FBMS
                    NASDAQ Equity,The First of Long Island Corporation (FLIC),FLIC
                    NASDAQ Equity,The Goodyear Tire & Rubber Company (GT),GT
                    NASDAQ Equity,"The Habit Restaurants, Inc. (HABT)",HABT
                    NASDAQ Equity,"The Hackett Group, Inc. (HCKT)",HCKT
                    NASDAQ Equity,"The Hain Celestial Group, Inc. (HAIN)",HAIN
                    NASDAQ Equity,"The Herzfeld Caribbean Basin Fund, Inc. (CUBA)",CUBA
                    NASDAQ Equity,The Intergroup Corporation (INTG),INTG
                    NASDAQ Equity,The Joint Corp. (JYNT),JYNT
                    NASDAQ Equity,The Kraft Heinz Company (KHC),KHC
                    NASDAQ Equity,The Long-Term Care ETF (OLD),OLD
                    NASDAQ Equity,The Lovesac Company (LOVE),LOVE
                    NASDAQ Equity,The Madison Square Garden Company (MSG),MSG
                    NASDAQ Equity,The Medicines Company (MDCO),MDCO
                    NASDAQ Equity,"The Meet Group, Inc. (MEET)",MEET
                    NASDAQ Equity,"The Michaels Companies, Inc. (MIK)",MIK
                    NASDAQ Equity,The Middleby Corporation (MIDD),MIDD
                    NASDAQ Equity,The Obesity ETF (SLIM),SLIM
                    NASDAQ Equity,"The ONE Group Hospitality, Inc. (STKS)",STKS
                    NASDAQ Equity,The Organics ETF (ORG),ORG
                    NASDAQ Equity,"The Peck Company, Inc. (PECK)",PECK
                    NASDAQ Equity,"The Peck Company, Inc. (PECKW)",PECKW
                    NASDAQ Equity,The Providence Service Corporation (PRSC),PRSC
                    NASDAQ Equity,The RMR Group Inc. (RMR),RMR
                    NASDAQ Equity,The Simply Good Foods Company (SMPL),SMPL
                    NASDAQ Equity,The Stars Group Inc. (TSG),TSG
                    NASDAQ Equity,"The Trade Desk, Inc. (TTD)",TTD
                    NASDAQ Equity,The York Water Company (YORW),YORW
                    NASDAQ Equity,The9 Limited (NCTY),NCTY
                    NASDAQ Equity,"TherapeuticsMD, Inc. (TXMD)",TXMD
                    NASDAQ Equity,Therapix Biosciences Ltd. (TRPX),TRPX
                    NASDAQ Equity,"Theravance Biopharma, Inc. (TBPH)",TBPH
                    NASDAQ Equity,"TheStreet, Inc. (TST)",TST
                    NASDAQ Equity,"THL Credit, Inc. (TCRD)",TCRD
                    NASDAQ Equity,"Thunder Bridge Acquisition, Ltd. (TBRG)",TBRG
                    NASDAQ Equity,"Thunder Bridge Acquisition, Ltd. (TBRGU)",TBRGU
                    NASDAQ Equity,"Thunder Bridge Acquisition, Ltd. (TBRGW)",TBRGW
                    NASDAQ Equity,Tiberius Acquisition Corporation (TIBR),TIBR
                    NASDAQ Equity,Tiberius Acquisition Corporation (TIBRU),TIBRU
                    NASDAQ Equity,Tiberius Acquisition Corporation (TIBRW),TIBRW
                    NASDAQ Equity,"Tile Shop Hldgs, Inc. (TTS)",TTS
                    NASDAQ Equity,"Tilray, Inc. (TLRY)",TLRY
                    NASDAQ Equity,"Timberland Bancorp, Inc. (TSBK)",TSBK
                    NASDAQ Equity,Tiptree Inc. (TIPT),TIPT
                    NASDAQ Equity,Titan Machinery Inc. (TITN),TITN
                    NASDAQ Equity,Titan Medical Inc. (TMDI),TMDI
                    NASDAQ Equity,"Titan Pharmaceuticals, Inc. (TTNP)",TTNP
                    NASDAQ Equity,"Tivity Health, Inc. (TVTY)",TVTY
                    NASDAQ Equity,TiVo Corporation (TIVO),TIVO
                    NASDAQ Equity,Tiziana Life Sciences plc (TLSA),TLSA
                    NASDAQ Equity,TKK Symphony Acquisition Corporation (TKKS),TKKS
                    NASDAQ Equity,TKK Symphony Acquisition Corporation (TKKSR),TKKSR
                    NASDAQ Equity,TKK Symphony Acquisition Corporation (TKKSU),TKKSU
                    NASDAQ Equity,TKK Symphony Acquisition Corporation (TKKSW),TKKSW
                    NASDAQ Equity,"T-Mobile US, Inc. (TMUS)",TMUS
                    NASDAQ Equity,TMSR Holding Company Limited (TMSR),TMSR
                    NASDAQ Equity,Tocagen Inc. (TOCA),TOCA
                    NASDAQ Equity,Tonix Pharmaceuticals Holding Corp. (TNXP),TNXP
                    NASDAQ Equity,TOP Ships Inc. (TOPS),TOPS
                    NASDAQ Equity,"Torchlight Energy Resources, Inc. (TRCH)",TRCH
                    NASDAQ Equity,TORM plc (TRMD),TRMD
                    NASDAQ Equity,Tottenham Acquisition I Limited (TOTA),TOTA
                    NASDAQ Equity,Tottenham Acquisition I Limited (TOTAR),TOTAR
                    NASDAQ Equity,Tottenham Acquisition I Limited (TOTAU),TOTAU
                    NASDAQ Equity,Tottenham Acquisition I Limited (TOTAW),TOTAW
                    NASDAQ Equity,"ToughBuilt Industries, Inc. (TBLT)",TBLT
                    NASDAQ Equity,"ToughBuilt Industries, Inc. (TBLTU)",TBLTU
                    NASDAQ Equity,"ToughBuilt Industries, Inc. (TBLTW)",TBLTW
                    NASDAQ Equity,Tower Semiconductor Ltd. (TSEM),TSEM
                    NASDAQ Equity,"Town Sports International Holdings, Inc. (CLUB)",CLUB
                    NASDAQ Equity,Towne Bank (TOWN),TOWN
                    NASDAQ Equity,"TPI Composites, Inc. (TPIC)",TPIC
                    NASDAQ Equity,"TRACON Pharmaceuticals, Inc. (TCON)",TCON
                    NASDAQ Equity,Tractor Supply Company (TSCO),TSCO
                    NASDAQ Equity,Tradeweb Markets Inc. (TW),TW
                    NASDAQ Equity,Trans World Entertainment Corp. (TWMC),TWMC
                    NASDAQ Equity,TransAct Technologies Incorporated (TACT),TACT
                    NASDAQ Equity,"Transcat, Inc. (TRNS)",TRNS
                    NASDAQ Equity,TransGlobe Energy Corporation (TGA),TGA
                    NASDAQ Equity,"Translate Bio, Inc. (TBIO)",TBIO
                    NASDAQ Equity,"TransMedics Group, Inc. (TMDX)",TMDX
                    NASDAQ Equity,TravelCenters of America LLC (TA),TA
                    NASDAQ Equity,TravelCenters of America LLC (TANNI),TANNI
                    NASDAQ Equity,TravelCenters of America LLC (TANNL),TANNL
                    NASDAQ Equity,TravelCenters of America LLC (TANNZ),TANNZ
                    NASDAQ Equity,Travelzoo (TZOO),TZOO
                    NASDAQ Equity,Tremont Mortgage Trust (TRMT),TRMT
                    NASDAQ Equity,"Trevena, Inc. (TRVN)",TRVN
                    NASDAQ Equity,"Trevi Therapeutics, Inc. (TRVI)",TRVI
                    NASDAQ Equity,Tribune Publishing Company (TPCO),TPCO
                    NASDAQ Equity,"Tricida, Inc. (TCDA)",TCDA
                    NASDAQ Equity,TriCo Bancshares (TCBK),TCBK
                    NASDAQ Equity,Trident Acquisitions Corp. (TDAC),TDAC
                    NASDAQ Equity,Trident Acquisitions Corp. (TDACU),TDACU
                    NASDAQ Equity,Trident Acquisitions Corp. (TDACW),TDACW
                    NASDAQ Equity,Trillium Therapeutics Inc. (TRIL),TRIL
                    NASDAQ Equity,TriMas Corporation (TRS),TRS
                    NASDAQ Equity,Trimble Inc. (TRMB),TRMB
                    NASDAQ Equity,Trinity Biotech plc (TRIB),TRIB
                    NASDAQ Equity,Trinity Merger Corp. (TMCX),TMCX
                    NASDAQ Equity,Trinity Merger Corp. (TMCXU),TMCXU
                    NASDAQ Equity,Trinity Merger Corp. (TMCXW),TMCXW
                    NASDAQ Equity,"TripAdvisor, Inc. (TRIP)",TRIP
                    NASDAQ Equity,"TriState Capital Holdings, Inc. (TSC)",TSC
                    NASDAQ Equity,"TriState Capital Holdings, Inc. (TSCAP)",TSCAP
                    NASDAQ Equity,"TriState Capital Holdings, Inc. (TSCBP)",TSCBP
                    NASDAQ Equity,"Triumph Bancorp, Inc. (TBK)",TBK
                    NASDAQ Equity,trivago N.V. (TRVG),TRVG
                    NASDAQ Equity,"TrovaGene, Inc. (TROV)",TROV
                    NASDAQ Equity,"TrueCar, Inc. (TRUE)",TRUE
                    NASDAQ Equity,"Trupanion, Inc. (TRUP)",TRUP
                    NASDAQ Equity,TrustCo Bank Corp NY (TRST),TRST
                    NASDAQ Equity,Trustmark Corporation (TRMK),TRMK
                    NASDAQ Equity,"TSR, Inc. (TSRI)",TSRI
                    NASDAQ Equity,"TTEC Holdings, Inc. (TTEC)",TTEC
                    NASDAQ Equity,"TTM Technologies, Inc. (TTMI)",TTMI
                    NASDAQ Equity,TuanChe Limited (TC),TC
                    NASDAQ Equity,Tucows Inc. (TCX),TCX
                    NASDAQ Equity,Tuesday Morning Corp. (TUES),TUES
                    NASDAQ Equity,Tuniu Corporation (TOUR),TOUR
                    NASDAQ Equity,"Turning Point Therapeutics, Inc. (TPTX)",TPTX
                    NASDAQ Equity,Turtle Beach Corporation (HEAR),HEAR
                    NASDAQ Equity,Tuscan Holdings Corp. (THCB),THCB
                    NASDAQ Equity,Tuscan Holdings Corp. (THCBU),THCBU
                    NASDAQ Equity,Tuscan Holdings Corp. (THCBW),THCBW
                    NASDAQ Equity,Twelve Seas Investment Company (BROG),BROG
                    NASDAQ Equity,Twelve Seas Investment Company (BROGR),BROGR
                    NASDAQ Equity,Twelve Seas Investment Company (BROGU),BROGU
                    NASDAQ Equity,Twelve Seas Investment Company (BROGW),BROGW
                    NASDAQ Equity,"Twin Disc, Incorporated (TWIN)",TWIN
                    NASDAQ Equity,Twist Bioscience Corporation (TWST),TWST
                    NASDAQ Equity,Two River Bancorp (TRCB),TRCB
                    NASDAQ Equity,"Tyme Technologies, Inc. (TYME)",TYME
                    NASDAQ Equity,"U S Concrete, Inc. (USCR)",USCR
                    NASDAQ Equity,"U.S. Auto Parts Network, Inc. (PRTS)",PRTS
                    NASDAQ Equity,U.S. Energy Corp. (USEG),USEG
                    NASDAQ Equity,"U.S. Global Investors, Inc. (GROW)",GROW
                    NASDAQ Equity,U.S. Gold Corp. (USAU),USAU
                    NASDAQ Equity,"U.S. Well Services, Inc. (USWS)",USWS
                    NASDAQ Equity,"U.S. Well Services, Inc. (USWSW)",USWSW
                    NASDAQ Equity,"Ubiquiti Networks, Inc. (UBNT)",UBNT
                    NASDAQ Equity,"UFP Technologies, Inc. (UFPT)",UFPT
                    NASDAQ Equity,"Ulta Beauty, Inc. (ULTA)",ULTA
                    NASDAQ Equity,"Ultra Clean Holdings, Inc. (UCTT)",UCTT
                    NASDAQ Equity,Ultra Petroleum Corp. (UPL),UPL
                    NASDAQ Equity,Ultragenyx Pharmaceutical Inc. (RARE),RARE
                    NASDAQ Equity,Ultralife Corporation (ULBI),ULBI
                    NASDAQ Equity,UMB Financial Corporation (UMBF),UMBF
                    NASDAQ Equity,Umpqua Holdings Corporation (UMPQ),UMPQ
                    NASDAQ Equity,Unico American Corporation (UNAM),UNAM
                    NASDAQ Equity,"Union Bankshares, Inc. (UNB)",UNB
                    NASDAQ Equity,uniQure N.V. (QURE),QURE
                    NASDAQ Equity,"United Bancorp, Inc. (UBCP)",UBCP
                    NASDAQ Equity,"United Bancshares, Inc. (UBOH)",UBOH
                    NASDAQ Equity,"United Bankshares, Inc. (UBSI)",UBSI
                    NASDAQ Equity,"United Community Banks, Inc. (UCBI)",UCBI
                    NASDAQ Equity,United Community Financial Corp. (UCFC),UCFC
                    NASDAQ Equity,"United Continental Holdings, Inc. (UAL)",UAL
                    NASDAQ Equity,"United Financial Bancorp, Inc.  (UBNK)",UBNK
                    NASDAQ Equity,"United Fire Group, Inc (UFCS)",UFCS
                    NASDAQ Equity,United Insurance Holdings Corp. (UIHC),UIHC
                    NASDAQ Equity,"United Natural Foods, Inc. (UNFI)",UNFI
                    NASDAQ Equity,United Security Bancshares (UBFO),UBFO
                    NASDAQ Equity,"United States Lime & Minerals, Inc. (USLM)",USLM
                    NASDAQ Equity,United Therapeutics Corporation (UTHR),UTHR
                    NASDAQ Equity,"United-Guardian, Inc. (UG)",UG
                    NASDAQ Equity,Uniti Group Inc. (UNIT),UNIT
                    NASDAQ Equity,"Unity Bancorp, Inc. (UNTY)",UNTY
                    NASDAQ Equity,"Unity Biotechnology, Inc. (UBX)",UBX
                    NASDAQ Equity,Universal Display Corporation (OLED),OLED
                    NASDAQ Equity,Universal Electronics Inc. (UEIC),UEIC
                    NASDAQ Equity,"Universal Forest Products, Inc. (UFPI)",UFPI
                    NASDAQ Equity,"Universal Logistics Holdings, Inc. (ULH)",ULH
                    NASDAQ Equity,"Universal Stainless & Alloy Products, Inc. (USAP)",USAP
                    NASDAQ Equity,Univest Financial Corporation (UVSP),UVSP
                    NASDAQ Equity,Unum Therapeutics Inc. (UMRX),UMRX
                    NASDAQ Equity,UP Fintech China-U.S. Internet Titans ETF (TTTN),TTTN
                    NASDAQ Equity,UP Fintech Holding Limited (TIGR),TIGR
                    NASDAQ Equity,"Upland Software, Inc. (UPLD)",UPLD
                    NASDAQ Equity,Upwork Inc. (UPWK),UPWK
                    NASDAQ Equity,"Urban One, Inc.  (UONE)",UONE
                    NASDAQ Equity,"Urban One, Inc.  (UONEK)",UONEK
                    NASDAQ Equity,"Urban Outfitters, Inc. (URBN)",URBN
                    NASDAQ Equity,"Urban Tea, Inc. (MYT)",MYT
                    NASDAQ Equity,UroGen Pharma Ltd. (URGN),URGN
                    NASDAQ Equity,Urovant Sciences Ltd. (UROV),UROV
                    NASDAQ Equity,"US Ecology, Inc. (ECOL)",ECOL
                    NASDAQ Equity,"USA Technologies, Inc. (USAT)",USAT
                    NASDAQ Equity,"USA Technologies, Inc. (USATP)",USATP
                    NASDAQ Equity,"USA Truck, Inc. (USAK)",USAK
                    NASDAQ Equity,"Utah Medical Products, Inc. (UTMD)",UTMD
                    NASDAQ Equity,UTStarcom Holdings Corp (UTSI),UTSI
                    NASDAQ Equity,Uxin Limited (UXIN),UXIN
                    NASDAQ Equity,"Vaccinex, Inc. (VCNX)",VCNX
                    NASDAQ Equity,"Valeritas Holdings, Inc. (VLRX)",VLRX
                    NASDAQ Equity,Validea Market Legends ETF (VALX),VALX
                    NASDAQ Equity,Valley National Bancorp (VLY),VLY
                    NASDAQ Equity,Valley National Bancorp (VLYPO),VLYPO
                    NASDAQ Equity,Valley National Bancorp (VLYPP),VLYPP
                    NASDAQ Equity,"Value Line, Inc. (VALU)",VALU
                    NASDAQ Equity,Vanda Pharmaceuticals Inc. (VNDA),VNDA
                    NASDAQ Equity,VanEck Vectors Biotech ETF (BBH),BBH
                    NASDAQ Equity,VanEck Vectors Pharmaceutical ETF (PPH),PPH
                    NASDAQ Equity,Vanguard Emerging Markets Government Bond ETF (VWOB),VWOB
                    NASDAQ Equity,Vanguard Global ex-U.S. Real Estate ETF (VNQI),VNQI
                    NASDAQ Equity,Vanguard Intermediate-Term Corporate Bond ETF (VCIT),VCIT
                    NASDAQ Equity,Vanguard Intermediate-Term Treasury ETF (VGIT),VGIT
                    NASDAQ Equity,Vanguard International Dividend Appreciation ETF (VIGI),VIGI
                    NASDAQ Equity,Vanguard International High Dividend Yield ETF (VYMI),VYMI
                    NASDAQ Equity,Vanguard Long-Term Corporate Bond ETF (VCLT),VCLT
                    NASDAQ Equity,Vanguard Long-Treasury ETF (VGLT),VGLT
                    NASDAQ Equity,Vanguard Mortgage-Backed Securities ETF (VMBS),VMBS
                    NASDAQ Equity,Vanguard Russell 1000 ETF (VONE),VONE
                    NASDAQ Equity,Vanguard Russell 1000 Growth ETF (VONG),VONG
                    NASDAQ Equity,Vanguard Russell 1000 Value ETF (VONV),VONV
                    NASDAQ Equity,Vanguard Russell 2000 ETF (VTWO),VTWO
                    NASDAQ Equity,Vanguard Russell 2000 Growth ETF (VTWG),VTWG
                    NASDAQ Equity,Vanguard Russell 2000 Value ETF (VTWV),VTWV
                    NASDAQ Equity,Vanguard Russell 3000 ETF (VTHR),VTHR
                    NASDAQ Equity,Vanguard Short-Term Corporate Bond ETF (VCSH),VCSH
                    NASDAQ Equity,Vanguard Short-Term Inflation-Protected Securities Index Fund (VTIP),VTIP
                    NASDAQ Equity,Vanguard Short-Term Treasury ETF (VGSH),VGSH
                    NASDAQ Equity,Vanguard Total Bond Market ETF (BND),BND
                    NASDAQ Equity,Vanguard Total Corporate Bond ETF (VTC),VTC
                    NASDAQ Equity,Vanguard Total International Bond ETF (BNDX),BNDX
                    NASDAQ Equity,Vanguard Total International Stock ETF (VXUS),VXUS
                    NASDAQ Equity,Vanguard Total World Bond ETF (BNDW),BNDW
                    NASDAQ Equity,Varex Imaging Corporation (VREX),VREX
                    NASDAQ Equity,"Varonis Systems, Inc. (VRNS)",VRNS
                    NASDAQ Equity,Vascular Biogenics Ltd. (VBLT),VBLT
                    NASDAQ Equity,"Vaxart, Inc. (VXRT)",VXRT
                    NASDAQ Equity,"VBI Vaccines, Inc. (VBIV)",VBIV
                    NASDAQ Equity,VectoIQ Acquisition Corp. (VTIQ),VTIQ
                    NASDAQ Equity,VectoIQ Acquisition Corp. (VTIQU),VTIQU
                    NASDAQ Equity,VectoIQ Acquisition Corp. (VTIQW),VTIQW
                    NASDAQ Equity,Veeco Instruments Inc. (VECO),VECO
                    NASDAQ Equity,VEON Ltd. (VEON),VEON
                    NASDAQ Equity,"Vera Bradley, Inc. (VRA)",VRA
                    NASDAQ Equity,"Veracyte, Inc. (VCYT)",VCYT
                    NASDAQ Equity,"Verastem, Inc. (VSTM)",VSTM
                    NASDAQ Equity,"Verb Technology Company, Inc. (VERB)",VERB
                    NASDAQ Equity,"Verb Technology Company, Inc. (VERBW)",VERBW
                    NASDAQ Equity,Vericel Corporation (VCEL),VCEL
                    NASDAQ Equity,Verint Systems Inc. (VRNT),VRNT
                    NASDAQ Equity,"VeriSign, Inc. (VRSN)",VRSN
                    NASDAQ Equity,"Verisk Analytics, Inc. (VRSK)",VRSK
                    NASDAQ Equity,"Veritex Holdings, Inc. (VBTX)",VBTX
                    NASDAQ Equity,"Veritone, Inc. (VERI)",VERI
                    NASDAQ Equity,"Vermillion, Inc. (VRML)",VRML
                    NASDAQ Equity,Verona Pharma plc (VRNA),VRNA
                    NASDAQ Equity,Verra Mobility Corporation (VRRM),VRRM
                    NASDAQ Equity,Verrica Pharmaceuticals Inc. (VRCA),VRCA
                    NASDAQ Equity,"Vertex Energy, Inc (VTNR)",VTNR
                    NASDAQ Equity,Vertex Pharmaceuticals Incorporated (VRTX),VRTX
                    NASDAQ Equity,Veru Inc. (VERU),VERU
                    NASDAQ Equity,Viacom Inc. (VIA),VIA
                    NASDAQ Equity,Viacom Inc. (VIAB),VIAB
                    NASDAQ Equity,"ViaSat, Inc. (VSAT)",VSAT
                    NASDAQ Equity,Viavi Solutions Inc. (VIAV),VIAV
                    NASDAQ Equity,Vical Incorporated (VICL),VICL
                    NASDAQ Equity,Vicor Corporation (VICR),VICR
                    NASDAQ Equity,"Victory Capital Holdings, Inc. (VCTR)",VCTR
                    NASDAQ Equity,VictoryShares Developed Enhanced Volatility Wtd ETF (CIZ),CIZ
                    NASDAQ Equity,VictoryShares Dividend Accelerator ETF (VSDA),VSDA
                    NASDAQ Equity,VictoryShares Emerging Market High Div Volatility Wtd ETF (CEY),CEY
                    NASDAQ Equity,VictoryShares Emerging Market Volatility Wtd ETF (CEZ),CEZ
                    NASDAQ Equity,VictoryShares International High Div Volatility Wtd ETF (CID),CID
                    NASDAQ Equity,VictoryShares International Volatility Wtd ETF (CIL),CIL
                    NASDAQ Equity,VictoryShares US 500 Enhanced Volatility Wtd ETF (CFO),CFO
                    NASDAQ Equity,VictoryShares US 500 Volatility Wtd ETF (CFA),CFA
                    NASDAQ Equity,VictoryShares US Discovery Enhanced Volatility Wtd ETF (CSF),CSF
                    NASDAQ Equity,VictoryShares US EQ Income Enhanced Volatility Wtd ETF (CDC),CDC
                    NASDAQ Equity,VictoryShares US Large Cap High Div Volatility Wtd ETF (CDL),CDL
                    NASDAQ Equity,VictoryShares US Multi-Factor Minimum Volatility ETF (VSMV),VSMV
                    NASDAQ Equity,VictoryShares US Small Cap High Div Volatility Wtd ETF (CSB),CSB
                    NASDAQ Equity,VictoryShares US Small Cap Volatility Wtd ETF (CSA),CSA
                    NASDAQ Equity,"ViewRay, Inc. (VRAY)",VRAY
                    NASDAQ Equity,"Viking Therapeutics, Inc. (VKTX)",VKTX
                    NASDAQ Equity,"Viking Therapeutics, Inc. (VKTXW)",VKTXW
                    NASDAQ Equity,Village Bank and Trust Financial Corp. (VBFC),VBFC
                    NASDAQ Equity,"Village Farms International, Inc. (VFF)",VFF
                    NASDAQ Equity,"Village Super Market, Inc. (VLGEA)",VLGEA
                    NASDAQ Equity,"Viomi Technology Co., Ltd (VIOT)",VIOT
                    NASDAQ Equity,Viper Energy Partners LP (VNOM),VNOM
                    NASDAQ Equity,Virco Manufacturing Corporation (VIRC),VIRC
                    NASDAQ Equity,"VirTra, Inc. (VTSI)",VTSI
                    NASDAQ Equity,"Virtu Financial, Inc. (VIRT)",VIRT
                    NASDAQ Equity,"Virtus Investment Partners, Inc. (VRTS)",VRTS
                    NASDAQ Equity,"Virtus Investment Partners, Inc. (VRTSP)",VRTSP
                    NASDAQ Equity,Virtus LifeSci Biotech Clinical Trials ETF (BBC),BBC
                    NASDAQ Equity,Virtus LifeSci Biotech Products ETF (BBP),BBP
                    NASDAQ Equity,Virtusa Corporation (VRTU),VRTU
                    NASDAQ Equity,"Vislink Technologies, Inc. (VISL)",VISL
                    NASDAQ Equity,"VistaGen Therapeutics, Inc. (VTGN)",VTGN
                    NASDAQ Equity,Visteon Corporation (VC),VC
                    NASDAQ Equity,"Viveve Medical, Inc. (VIVE)",VIVE
                    NASDAQ Equity,VivoPower International PLC (VVPR),VVPR
                    NASDAQ Equity,"VIVUS, Inc. (VVUS)",VVUS
                    NASDAQ Equity,Vodafone Group Plc (VOD),VOD
                    NASDAQ Equity,VOXX International Corporation (VOXX),VOXX
                    NASDAQ Equity,"Voyager Therapeutics, Inc. (VYGR)",VYGR
                    NASDAQ Equity,VSE Corporation (VSEC),VSEC
                    NASDAQ Equity,vTv Therapeutics Inc. (VTVT),VTVT
                    NASDAQ Equity,Vuzix Corporation (VUZI),VUZI
                    NASDAQ Equity,Wah Fu Education Group Limited (WAFU),WAFU
                    NASDAQ Equity,Waitr Holdings Inc. (WTRH),WTRH
                    NASDAQ Equity,"Walgreens Boots Alliance, Inc. (WBA)",WBA
                    NASDAQ Equity,"Washington Federal, Inc. (WAFD)",WAFD
                    NASDAQ Equity,"Washington Trust Bancorp, Inc. (WASH)",WASH
                    NASDAQ Equity,"Waterstone Financial, Inc. (WSBF)",WSBF
                    NASDAQ Equity,Watford Holdings Ltd. (WTRE),WTRE
                    NASDAQ Equity,WAVE Life Sciences Ltd. (WVE),WVE
                    NASDAQ Equity,"Wayside Technology Group, Inc. (WSTG)",WSTG
                    NASDAQ Equity,"WCF Bancorp, Inc. (WCFB)",WCFB
                    NASDAQ Equity,WD-40 Company (WDFC),WDFC
                    NASDAQ Equity,Wealthbridge Acquisition Limited (HHHH),HHHH
                    NASDAQ Equity,Wealthbridge Acquisition Limited (HHHHR),HHHHR
                    NASDAQ Equity,Wealthbridge Acquisition Limited (HHHHU),HHHHU
                    NASDAQ Equity,Wealthbridge Acquisition Limited (HHHHW),HHHHW
                    NASDAQ Equity,Weibo Corporation (WB),WB
                    NASDAQ Equity,Weight Watchers International Inc (WW),WW
                    NASDAQ Equity,"Wellesley Bancorp, Inc. (WEBK)",WEBK
                    NASDAQ Equity,Wendy&#39;s Company (The) (WEN),WEN
                    NASDAQ Equity,"Werner Enterprises, Inc. (WERN)",WERN
                    NASDAQ Equity,"WesBanco, Inc. (WSBC)",WSBC
                    NASDAQ Equity,West Bancorporation (WTBA),WTBA
                    NASDAQ Equity,Westamerica Bancorporation (WABC),WABC
                    NASDAQ Equity,"Westell Technologies, Inc. (WSTL)",WSTL
                    NASDAQ Equity,Western Asset Short Duration Income ETF (WINC),WINC
                    NASDAQ Equity,Western Asset Total Return ETF (WBND),WBND
                    NASDAQ Equity,Western Digital Corporation (WDC),WDC
                    NASDAQ Equity,"Western New England Bancorp, Inc. (WNEB)",WNEB
                    NASDAQ Equity,Westport Fuel Systems Inc (WPRT),WPRT
                    NASDAQ Equity,"Westwater Resources, Inc. (WWR)",WWR
                    NASDAQ Equity,"Weyco Group, Inc. (WEYS)",WEYS
                    NASDAQ Equity,"Wheeler Real Estate Investment Trust, Inc. (WHLR)",WHLR
                    NASDAQ Equity,"Wheeler Real Estate Investment Trust, Inc. (WHLRD)",WHLRD
                    NASDAQ Equity,"Wheeler Real Estate Investment Trust, Inc. (WHLRP)",WHLRP
                    NASDAQ Equity,"WhiteHorse Finance, Inc. (WHF)",WHF
                    NASDAQ Equity,"WhiteHorse Finance, Inc. (WHFBZ)",WHFBZ
                    NASDAQ Equity,"Wilhelmina International, Inc. (WHLM)",WHLM
                    NASDAQ Equity,"Willamette Valley Vineyards, Inc. (WVVI)",WVVI
                    NASDAQ Equity,"Willamette Valley Vineyards, Inc. (WVVIP)",WVVIP
                    NASDAQ Equity,"Willdan Group, Inc. (WLDN)",WLDN
                    NASDAQ Equity,Willis Lease Finance Corporation (WLFC),WLFC
                    NASDAQ Equity,Willis Towers Watson Public Limited Company (WLTW),WLTW
                    NASDAQ Equity,WillScot Corporation (WSC),WSC
                    NASDAQ Equity,Wingstop Inc. (WING),WING
                    NASDAQ Equity,Winmark Corporation (WINA),WINA
                    NASDAQ Equity,Wins Finance Holdings Inc. (WINS),WINS
                    NASDAQ Equity,Wintrust Financial Corporation (WTFC),WTFC
                    NASDAQ Equity,Wintrust Financial Corporation (WTFCM),WTFCM
                    NASDAQ Equity,WisdomTree Barclays Negative Duration U.S. Aggregate Bond Fund (AGND),AGND
                    NASDAQ Equity,WisdomTree China ex-State-Owned Enterprises Fund (CXSE),CXSE
                    NASDAQ Equity,WisdomTree Emerging Markets Consumer Growth Fund (EMCG),EMCG
                    NASDAQ Equity,WisdomTree Emerging Markets Corporate Bond Fund (EMCB),EMCB
                    NASDAQ Equity,WisdomTree Emerging Markets Quality Dividend Growth Fund (DGRE),DGRE
                    NASDAQ Equity,WisdomTree Germany Hedged Equity Fund (DXGE),DXGE
                    NASDAQ Equity,WisdomTree Interest Rate Hedged High Yield Bond Fund (HYZD),HYZD
                    NASDAQ Equity,WisdomTree Interest Rate Hedged U.S. Aggregate Bond Fund (AGZD),AGZD
                    NASDAQ Equity,"WisdomTree Investments, Inc. (WETF)",WETF
                    NASDAQ Equity,WisdomTree Japan Hedged SmallCap Equity Fund (DXJS),DXJS
                    NASDAQ Equity,WisdomTree Middle East Dividend Fund (GULF),GULF
                    NASDAQ Equity,WisdomTree Negative Duration High Yield Bond Fund (HYND),HYND
                    NASDAQ Equity,WisdomTree U.S. Quality Dividend Growth Fund (DGRW),DGRW
                    NASDAQ Equity,WisdomTree U.S. SmallCap Quality Dividend Growth Fund (DGRS),DGRS
                    NASDAQ Equity,Wix.com Ltd. (WIX),WIX
                    NASDAQ Equity,"Woodward, Inc. (WWD)",WWD
                    NASDAQ Equity,"Workday, Inc. (WDAY)",WDAY
                    NASDAQ Equity,"Workhorse Group, Inc. (WKHS)",WKHS
                    NASDAQ Equity,World Acceptance Corporation (WRLD),WRLD
                    NASDAQ Equity,"Wrap Technologies, Inc. (WRTC)",WRTC
                    NASDAQ Equity,Wright Medical Group N.V. (WMGI),WMGI
                    NASDAQ Equity,WSFS Financial Corporation (WSFS),WSFS
                    NASDAQ Equity,WVS Financial Corp. (WVFC),WVFC
                    NASDAQ Equity,"Wynn Resorts, Limited (WYNN)",WYNN
                    NASDAQ Equity,"X4 Pharmaceuticals, Inc. (XFOR)",XFOR
                    NASDAQ Equity,XBiotech Inc. (XBIT),XBIT
                    NASDAQ Equity,"Xcel Brands, Inc (XELB)",XELB
                    NASDAQ Equity,Xcel Energy Inc. (XEL),XEL
                    NASDAQ Equity,"Xencor, Inc. (XNCR)",XNCR
                    NASDAQ Equity,"Xenetic Biosciences, Inc. (XBIO)",XBIO
                    NASDAQ Equity,Xenon Pharmaceuticals Inc. (XENE),XENE
                    NASDAQ Equity,"Xeris Pharmaceuticals, Inc. (XERS)",XERS
                    NASDAQ Equity,"Xilinx, Inc. (XLNX)",XLNX
                    NASDAQ Equity,XOMA Corporation (XOMA),XOMA
                    NASDAQ Equity,Xperi Corporation (XPER),XPER
                    NASDAQ Equity,"XpresSpa Group, Inc.  (XSPA)",XSPA
                    NASDAQ Equity,XTL Biopharmaceuticals Ltd. (XTLB),XTLB
                    NASDAQ Equity,Xunlei Limited (XNET),XNET
                    NASDAQ Equity,"Xynomic Pharmaceuticals Holdings, Inc. (XYN)",XYN
                    NASDAQ Equity,"Xynomic Pharmaceuticals Holdings, Inc. (XYNPW)",XYNPW
                    NASDAQ Equity,Yandex N.V. (YNDX),YNDX
                    NASDAQ Equity,Yangtze River Port and Logistics Limited  (YRIV),YRIV
                    NASDAQ Equity,"Yatra Online, Inc. (YTRA)",YTRA
                    NASDAQ Equity,"Yield10 Bioscience, Inc. (YTEN)",YTEN
                    NASDAQ Equity,Yintech Investment Holdings Limited (YIN),YIN
                    NASDAQ Equity,"Y-mAbs Therapeutics, Inc. (YMAB)",YMAB
                    NASDAQ Equity,"YogaWorks, Inc. (YOGA)",YOGA
                    NASDAQ Equity,"Youngevity International, Inc. (YGYI)",YGYI
                    NASDAQ Equity,"YRC Worldwide, Inc. (YRCW)",YRCW
                    NASDAQ Equity,Yunji Inc. (YJ),YJ
                    NASDAQ Equity,YY Inc. (YY),YY
                    NASDAQ Equity,"Zafgen, Inc. (ZFGN)",ZFGN
                    NASDAQ Equity,ZAGG Inc (ZAGG),ZAGG
                    NASDAQ Equity,Zai Lab Limited (ZLAB),ZLAB
                    NASDAQ Equity,Zealand Pharma A/S (ZEAL),ZEAL
                    NASDAQ Equity,Zebra Technologies Corporation (ZBRA),ZBRA
                    NASDAQ Equity,"Zillow Group, Inc. (Z)",Z
                    NASDAQ Equity,"Zillow Group, Inc. (ZG)",ZG
                    NASDAQ Equity,Zion Oil & Gas Inc (ZN),ZN
                    NASDAQ Equity,Zion Oil & Gas Inc (ZNWAA),ZNWAA
                    NASDAQ Equity,Zions Bancorporation N.A. (ZION),ZION
                    NASDAQ Equity,Zions Bancorporation N.A. (ZIONW),ZIONW
                    NASDAQ Equity,ZIOPHARM Oncology Inc (ZIOP),ZIOP
                    NASDAQ Equity,Zix Corporation (ZIXI),ZIXI
                    NASDAQ Equity,"ZK International Group Co., Ltd (ZKIN)",ZKIN
                    NASDAQ Equity,"Zogenix, Inc. (ZGNX)",ZGNX
                    NASDAQ Equity,"Zoom Video Communications, Inc. (ZM)",ZM
                    NASDAQ Equity,Zosano Pharma Corporation (ZSAN),ZSAN
                    NASDAQ Equity,Zovio Inc. (ZVO),ZVO
                    NASDAQ Equity,"Zscaler, Inc. (ZS)",ZS
                    NASDAQ Equity,Zumiez Inc. (ZUMZ),ZUMZ
                    NASDAQ Equity,"Zynerba Pharmaceuticals, Inc. (ZYNE)",ZYNE
                    NASDAQ Equity,"Zynex, Inc. (ZYXI)",ZYXI
                    NASDAQ Equity,Zynga Inc. (ZNGA),ZNGA
                    NYSE Equity,3D Systems Corporation (DDD),DDD
                    NYSE Equity,3M Company (MMM),MMM
                    NYSE Equity,500.com Limited (WBAI),WBAI
                    NYSE Equity,58.com Inc. (WUBA),WUBA
                    NYSE Equity,8x8 Inc (EGHT),EGHT
                    NYSE Equity,A.H. Belo Corporation (AHC),AHC
                    NYSE Equity,A.O Smith Corporation (AOS),AOS
                    NYSE Equity,"A10 Networks, Inc. (ATEN)",ATEN
                    NYSE Equity,"AAC Holdings, Inc. (AAC)",AAC
                    NYSE Equity,AAR Corp. (AIR),AIR
                    NYSE Equity,"Aaron&#39;s,  Inc. (AAN)",AAN
                    NYSE Equity,ABB Ltd (ABB),ABB
                    NYSE Equity,Abbott Laboratories (ABT),ABT
                    NYSE Equity,AbbVie Inc. (ABBV),ABBV
                    NYSE Equity,Abercrombie & Fitch Company (ANF),ANF
                    NYSE Equity,Aberdeen Global Dynamic Dividend Fund (AGD),AGD
                    NYSE Equity,Aberdeen Global Premier Properties Fund (AWP),AWP
                    NYSE Equity,Aberdeen Income Credit Strategies Fund (ACP),ACP
                    NYSE Equity,"Aberdeen Japan Equity Fund, Inc.  (JEQ)",JEQ
                    NYSE Equity,Aberdeen Total Dynamic Dividend Fund (AOD),AOD
                    NYSE Equity,ABM Industries Incorporated (ABM),ABM
                    NYSE Equity,Acadia Realty Trust (AKR),AKR
                    NYSE Equity,Accenture plc (ACN),ACN
                    NYSE Equity,Acco Brands Corporation (ACCO),ACCO
                    NYSE Equity,"Acorn International, Inc. (ATV)",ATV
                    NYSE Equity,Actuant Corporation (ATU),ATU
                    NYSE Equity,"Acuity Brands, Inc.  (AYI)",AYI
                    NYSE Equity,Acushnet Holdings Corp. (GOLF),GOLF
                    NYSE Equity,"Adams Diversified Equity Fund, Inc. (ADX)",ADX
                    NYSE Equity,"Adams Natural Resources Fund, Inc. (PEO)",PEO
                    NYSE Equity,Adecoagro S.A. (AGRO),AGRO
                    NYSE Equity,Adient plc (ADNT),ADNT
                    NYSE Equity,ADT Inc. (ADT),ADT
                    NYSE Equity,Adtalem Global Education Inc. (ATGE),ATGE
                    NYSE Equity,Advance Auto Parts Inc (AAP),AAP
                    NYSE Equity,"Advanced Disposal Services, Inc. (ADSW)",ADSW
                    NYSE Equity,"Advanced Drainage Systems, Inc. (WMS)",WMS
                    NYSE Equity,AdvanSix Inc. (ASIX),ASIX
                    NYSE Equity,Advent Claymore Convertible Securities and Income Fund (AVK),AVK
                    NYSE Equity,AECOM (ACM),ACM
                    NYSE Equity,Aegon NV (AEB),AEB
                    NYSE Equity,Aegon NV (AEG),AEG
                    NYSE Equity,Aegon NV (AEH),AEH
                    NYSE Equity,Aercap Holdings N.V. (AER),AER
                    NYSE Equity,"Aerohive Networks, Inc. (HIVE)",HIVE
                    NYSE Equity,"Aerojet Rocketdyne Holdings, Inc.  (AJRD)",AJRD
                    NYSE Equity,"Affiliated Managers Group, Inc. (AMG)",AMG
                    NYSE Equity,"Affiliated Managers Group, Inc. (MGR)",MGR
                    NYSE Equity,Aflac Incorporated (AFL),AFL
                    NYSE Equity,"AG Mortgage Investment Trust, Inc. (MITT)",MITT
                    NYSE Equity,"AG Mortgage Investment Trust, Inc. (MITT^A)",MITT^A
                    NYSE Equity,"AG Mortgage Investment Trust, Inc. (MITT^B)",MITT^B
                    NYSE Equity,AGCO Corporation (AGCO),AGCO
                    NYSE Equity,"Agilent Technologies, Inc. (A)",A
                    NYSE Equity,Agnico Eagle Mines Limited (AEM),AEM
                    NYSE Equity,Agree Realty Corporation (ADC),ADC
                    NYSE Equity,Air Lease Corporation (AL),AL
                    NYSE Equity,Air Lease Corporation (AL^A),AL^A
                    NYSE Equity,"Air Products and Chemicals, Inc. (APD)",APD
                    NYSE Equity,Aircastle Limited (AYR),AYR
                    NYSE Equity,AK Steel Holding Corporation (AKS),AKS
                    NYSE Equity,Alabama Power Company (ALP^Q),ALP^Q
                    NYSE Equity,"Alamo Group, Inc. (ALG)",ALG
                    NYSE Equity,Alamos Gold Inc. (AGI),AGI
                    NYSE Equity,"Alaska Air Group, Inc. (ALK)",ALK
                    NYSE Equity,Albany International Corporation (AIN),AIN
                    NYSE Equity,Albemarle Corporation (ALB),ALB
                    NYSE Equity,Alcoa Corporation (AA),AA
                    NYSE Equity,Alcon Inc. (ALC),ALC
                    NYSE Equity,"Alexander & Baldwin, Inc. (ALEX)",ALEX
                    NYSE Equity,"Alexander&#39;s, Inc. (ALX)",ALX
                    NYSE Equity,"Alexandria Real Estate Equities, Inc. (ARE)",ARE
                    NYSE Equity,"Alexandria Real Estate Equities, Inc. (ARE^D)",ARE^D
                    NYSE Equity,Algonquin Power & Utilities Corp. (AQN),AQN
                    NYSE Equity,Algonquin Power & Utilities Corp. (AQNA),AQNA
                    NYSE Equity,Algonquin Power & Utilities Corp. (AQNB),AQNB
                    NYSE Equity,Alibaba Group Holding Limited (BABA),BABA
                    NYSE Equity,Alleghany Corporation (Y),Y
                    NYSE Equity,Allegheny Technologies Incorporated (ATI),ATI
                    NYSE Equity,Allegion plc (ALLE),ALLE
                    NYSE Equity,Allergan plc. (AGN),AGN
                    NYSE Equity,"Allete, Inc. (ALE)",ALE
                    NYSE Equity,Alliance Data Systems Corporation (ADS),ADS
                    NYSE Equity,Alliance National Municipal Income Fund Inc (AFB),AFB
                    NYSE Equity,Alliance World Dollar Government Fund II (AWF),AWF
                    NYSE Equity,AllianceBernstein Holding L.P. (AB),AB
                    NYSE Equity,AllianzGI Convertible & Income 2024 Target Term Fund (CBH),CBH
                    NYSE Equity,AllianzGI Convertible & Income Fund (NCV),NCV
                    NYSE Equity,AllianzGI Convertible & Income Fund (NCV^A),NCV^A
                    NYSE Equity,AllianzGI Convertible & Income Fund II (NCZ),NCZ
                    NYSE Equity,AllianzGI Convertible & Income Fund II (NCZ^A),NCZ^A
                    NYSE Equity,AllianzGI Diversified Income & Convertible Fund (ACV),ACV
                    NYSE Equity,AllianzGI Equity & Convertible Income Fund (NIE),NIE
                    NYSE Equity,"AllianzGI NFJ Dividend, Interest & Premium Strategy Fund (NFJ)",NFJ
                    NYSE Equity,"Allison Transmission Holdings, Inc. (ALSN)",ALSN
                    NYSE Equity,Allstate Corporation (The) (ALL),ALL
                    NYSE Equity,Allstate Corporation (The) (ALL^A),ALL^A
                    NYSE Equity,Allstate Corporation (The) (ALL^B),ALL^B
                    NYSE Equity,Allstate Corporation (The) (ALL^D),ALL^D
                    NYSE Equity,Allstate Corporation (The) (ALL^E),ALL^E
                    NYSE Equity,Allstate Corporation (The) (ALL^F),ALL^F
                    NYSE Equity,Allstate Corporation (The) (ALL^G),ALL^G
                    NYSE Equity,Ally Financial Inc. (ALLY),ALLY
                    NYSE Equity,Ally Financial Inc. (ALLY^A),ALLY^A
                    NYSE Equity,"Alteryx, Inc. (AYX)",AYX
                    NYSE Equity,"Altice USA, Inc. (ATUS)",ATUS
                    NYSE Equity,Altria Group (MO),MO
                    NYSE Equity,Aluminum Corporation of China Limited (ACH),ACH
                    NYSE Equity,"Amber Road, Inc. (AMBR)",AMBR
                    NYSE Equity,Ambev S.A. (ABEV),ABEV
                    NYSE Equity,"AMC Entertainment Holdings, Inc. (AMC)",AMC
                    NYSE Equity,Amcor plc (AMCR),AMCR
                    NYSE Equity,Ameren Corporation (AEE),AEE
                    NYSE Equity,"Ameresco, Inc. (AMRC)",AMRC
                    NYSE Equity,"America Movil, S.A.B. de C.V. (AMOV)",AMOV
                    NYSE Equity,"America Movil, S.A.B. de C.V. (AMX)",AMX
                    NYSE Equity,"American Assets Trust, Inc. (AAT)",AAT
                    NYSE Equity,"American Axle & Manufacturing Holdings, Inc. (AXL)",AXL
                    NYSE Equity,American Campus Communities Inc (ACC),ACC
                    NYSE Equity,"American Eagle Outfitters, Inc. (AEO)",AEO
                    NYSE Equity,"American Electric Power Company, Inc. (AEP)",AEP
                    NYSE Equity,"American Electric Power Company, Inc. (AEP^B)",AEP^B
                    NYSE Equity,American Equity Investment Life Holding Company (AEL),AEL
                    NYSE Equity,American Express Company (AXP),AXP
                    NYSE Equity,"American Financial Group, Inc. (AFG)",AFG
                    NYSE Equity,"American Financial Group, Inc. (AFGB)",AFGB
                    NYSE Equity,"American Financial Group, Inc. (AFGE)",AFGE
                    NYSE Equity,"American Financial Group, Inc. (AFGH)",AFGH
                    NYSE Equity,American Homes 4 Rent (AMH),AMH
                    NYSE Equity,American Homes 4 Rent (AMH^D),AMH^D
                    NYSE Equity,American Homes 4 Rent (AMH^E),AMH^E
                    NYSE Equity,American Homes 4 Rent (AMH^F),AMH^F
                    NYSE Equity,American Homes 4 Rent (AMH^G),AMH^G
                    NYSE Equity,American Homes 4 Rent (AMH^H),AMH^H
                    NYSE Equity,"American International Group, Inc. (AIG)",AIG
                    NYSE Equity,"American International Group, Inc. (AIG.WS)",AIG.WS
                    NYSE Equity,"American International Group, Inc. (AIG^A)",AIG^A
                    NYSE Equity,"American Midstream Partners, LP (AMID)",AMID
                    NYSE Equity,"American Realty Investors, Inc. (ARL)",ARL
                    NYSE Equity,"American Renal Associates Holdings, Inc (ARA)",ARA
                    NYSE Equity,American States Water Company (AWR),AWR
                    NYSE Equity,American Tower Corporation (REIT) (AMT),AMT
                    NYSE Equity,American Vanguard Corporation (AVD),AVD
                    NYSE Equity,American Water Works (AWK),AWK
                    NYSE Equity,Americold Realty Trust (COLD),COLD
                    NYSE Equity,"AmeriGas Partners, L.P. (APU)",APU
                    NYSE Equity,"AMERIPRISE FINANCIAL SERVICES, INC. (AMP)",AMP
                    NYSE Equity,AmerisourceBergen Corporation (Holding Co) (ABC),ABC
                    NYSE Equity,Amira Nature Foods Ltd (ANFI),ANFI
                    NYSE Equity,AMN Healthcare Services Inc (AMN),AMN
                    NYSE Equity,"Amneal Pharmaceuticals, Inc. (AMRX)",AMRX
                    NYSE Equity,Ampco-Pittsburgh Corporation (AP),AP
                    NYSE Equity,Amphenol Corporation (APH),APH
                    NYSE Equity,AMREP Corporation (AXR),AXR
                    NYSE Equity,"AMTEK, Inc. (AME)",AME
                    NYSE Equity,Anadarko Petroleum Corporation (APC),APC
                    NYSE Equity,"Anaplan, Inc. (PLAN)",PLAN
                    NYSE Equity,Andeavor Logistics LP (ANDX),ANDX
                    NYSE Equity,Angel Oak Financial Strategies Income Term Trust (FINS),FINS
                    NYSE Equity,AngloGold Ashanti Limited (AU),AU
                    NYSE Equity,Anheuser-Busch Inbev SA (BUD),BUD
                    NYSE Equity,Anixter International Inc. (AXE),AXE
                    NYSE Equity,Annaly Capital Management Inc (NLY),NLY
                    NYSE Equity,Annaly Capital Management Inc (NLY^C.CL),NLY^C.CL
                    NYSE Equity,Annaly Capital Management Inc (NLY^D),NLY^D
                    NYSE Equity,Annaly Capital Management Inc (NLY^F),NLY^F
                    NYSE Equity,Annaly Capital Management Inc (NLY^G),NLY^G
                    NYSE Equity,Antero Midstream Corporation (AM),AM
                    NYSE Equity,Antero Resources Corporation (AR),AR
                    NYSE Equity,"Anthem, Inc. (ANTM)",ANTM
                    NYSE Equity,Anworth Mortgage Asset  Corporation (ANH),ANH
                    NYSE Equity,Anworth Mortgage Asset  Corporation (ANH^A),ANH^A
                    NYSE Equity,Anworth Mortgage Asset  Corporation (ANH^B),ANH^B
                    NYSE Equity,Anworth Mortgage Asset  Corporation (ANH^C),ANH^C
                    NYSE Equity,Aon plc (AON),AON
                    NYSE Equity,Apache Corporation (APA),APA
                    NYSE Equity,Apartment Investment and Management Company (AIV),AIV
                    NYSE Equity,Apergy Corporation (APY),APY
                    NYSE Equity,Aphria Inc. (APHA),APHA
                    NYSE Equity,Apollo Commercial Real Estate Finance (ARI),ARI
                    NYSE Equity,"Apollo Global Management, LLC (APO)",APO
                    NYSE Equity,"Apollo Global Management, LLC (APO^A)",APO^A
                    NYSE Equity,"Apollo Global Management, LLC (APO^B)",APO^B
                    NYSE Equity,Apollo Investment Corporation (AIY),AIY
                    NYSE Equity,Apollo Senior Floating Rate Fund Inc. (AFT),AFT
                    NYSE Equity,Apollo Tactical Income Fund Inc. (AIF),AIF
                    NYSE Equity,"Apple Hospitality REIT, Inc. (APLE)",APLE
                    NYSE Equity,"Applied Industrial Technologies, Inc. (AIT)",AIT
                    NYSE Equity,"AptarGroup, Inc. (ATR)",ATR
                    NYSE Equity,Aptiv PLC (APTV),APTV
                    NYSE Equity,"Aqua America, Inc. (WTR)",WTR
                    NYSE Equity,"Aqua America, Inc. (WTRU)",WTRU
                    NYSE Equity,Aquantia Corp. (AQ),AQ
                    NYSE Equity,AquaVenture Holdings Limited (WAAS),WAAS
                    NYSE Equity,Aramark (ARMK),ARMK
                    NYSE Equity,Arbor Realty Trust (ABR),ABR
                    NYSE Equity,Arbor Realty Trust (ABR^A),ABR^A
                    NYSE Equity,Arbor Realty Trust (ABR^B),ABR^B
                    NYSE Equity,Arbor Realty Trust (ABR^C),ABR^C
                    NYSE Equity,"ARC Document Solutions, Inc. (ARC)",ARC
                    NYSE Equity,ArcelorMittal (MT),MT
                    NYSE Equity,"Arch Coal, Inc. (ARCH)",ARCH
                    NYSE Equity,Archer-Daniels-Midland Company (ADM),ADM
                    NYSE Equity,"Archrock, Inc. (AROC)",AROC
                    NYSE Equity,Arconic Inc. (ARNC),ARNC
                    NYSE Equity,Arcos Dorados Holdings Inc. (ARCO),ARCO
                    NYSE Equity,"Arcosa, Inc. (ACA)",ACA
                    NYSE Equity,"Arcus Biosciences, Inc. (RCUS)",RCUS
                    NYSE Equity,Ardagh Group S.A. (ARD),ARD
                    NYSE Equity,Ardmore Shipping Corporation (ASC),ASC
                    NYSE Equity,Ares Capital Corporation (AFC),AFC
                    NYSE Equity,Ares Commercial Real Estate Corporation (ACRE),ACRE
                    NYSE Equity,"Ares Dynamic Credit Allocation Fund, Inc. (ARDC)",ARDC
                    NYSE Equity,Ares Management Corporation (ARES),ARES
                    NYSE Equity,Ares Management Corporation (ARES^A),ARES^A
                    NYSE Equity,"Argan, Inc. (AGX)",AGX
                    NYSE Equity,"Argo Group International Holdings, Ltd. (ARGD)",ARGD
                    NYSE Equity,"Argo Group International Holdings, Ltd. (ARGO)",ARGO
                    NYSE Equity,"Arista Networks, Inc. (ANET)",ANET
                    NYSE Equity,Arlington Asset Investment Corp (AI),AI
                    NYSE Equity,Arlington Asset Investment Corp (AI^B),AI^B
                    NYSE Equity,Arlington Asset Investment Corp (AI^C),AI^C
                    NYSE Equity,Arlington Asset Investment Corp (AIC),AIC
                    NYSE Equity,Arlington Asset Investment Corp (AIW),AIW
                    NYSE Equity,"Arlo Technologies, Inc. (ARLO)",ARLO
                    NYSE Equity,"Armada Hoffler Properties, Inc. (AHH)",AHH
                    NYSE Equity,"Armada Hoffler Properties, Inc. (AHH^A)",AHH^A
                    NYSE Equity,"ARMOUR Residential REIT, Inc. (ARR)",ARR
                    NYSE Equity,"ARMOUR Residential REIT, Inc. (ARR^A.CL)",ARR^A.CL
                    NYSE Equity,"ARMOUR Residential REIT, Inc. (ARR^B)",ARR^B
                    NYSE Equity,"Armstrong Flooring, Inc. (AFI)",AFI
                    NYSE Equity,Armstrong World Industries Inc (AWI),AWI
                    NYSE Equity,"Arrow Electronics, Inc. (ARW)",ARW
                    NYSE Equity,Arthur J. Gallagher & Co. (AJG),AJG
                    NYSE Equity,Artisan Partners Asset Management Inc. (APAM),APAM
                    NYSE Equity,ASA Gold and Precious Metals Limited (ASA),ASA
                    NYSE Equity,Asbury Automotive Group Inc (ABG),ABG
                    NYSE Equity,"ASE Technology Holding Co., Ltd. (ASX)",ASX
                    NYSE Equity,ASGN Incorporated (ASGN),ASGN
                    NYSE Equity,Ashford Hospitality Trust Inc (AHT),AHT
                    NYSE Equity,Ashford Hospitality Trust Inc (AHT^D),AHT^D
                    NYSE Equity,Ashford Hospitality Trust Inc (AHT^F),AHT^F
                    NYSE Equity,Ashford Hospitality Trust Inc (AHT^G),AHT^G
                    NYSE Equity,Ashford Hospitality Trust Inc (AHT^H),AHT^H
                    NYSE Equity,Ashford Hospitality Trust Inc (AHT^I),AHT^I
                    NYSE Equity,Ashland Global Holdings Inc. (ASH),ASH
                    NYSE Equity,"Aspen Aerogels, Inc. (ASPN)",ASPN
                    NYSE Equity,Aspen Insurance Holdings Limited (AHL^C),AHL^C
                    NYSE Equity,Aspen Insurance Holdings Limited (AHL^D),AHL^D
                    NYSE Equity,Associated Banc-Corp (ASB),ASB
                    NYSE Equity,Associated Banc-Corp (ASB^C),ASB^C
                    NYSE Equity,Associated Banc-Corp (ASB^D),ASB^D
                    NYSE Equity,Associated Banc-Corp (ASB^E),ASB^E
                    NYSE Equity,"Associated Capital Group, Inc. (AC)",AC
                    NYSE Equity,"Assurant, Inc. (AIZ)",AIZ
                    NYSE Equity,"Assurant, Inc. (AIZP)",AIZP
                    NYSE Equity,Assured Guaranty Ltd. (AGO),AGO
                    NYSE Equity,Assured Guaranty Ltd. (AGO^B),AGO^B
                    NYSE Equity,Assured Guaranty Ltd. (AGO^E),AGO^E
                    NYSE Equity,Assured Guaranty Ltd. (AGO^F),AGO^F
                    NYSE Equity,Astrazeneca PLC (AZN),AZN
                    NYSE Equity,At Home Group Inc. (HOME),HOME
                    NYSE Equity,AT&T Inc. (T),T
                    NYSE Equity,AT&T Inc. (TBB),TBB
                    NYSE Equity,AT&T Inc. (TBC),TBC
                    NYSE Equity,Atento S.A. (ATTO),ATTO
                    NYSE Equity,Athene Holding Ltd. (ATH),ATH
                    NYSE Equity,Athene Holding Ltd. (ATH^A),ATH^A
                    NYSE Equity,Atkore International Group Inc. (ATKR),ATKR
                    NYSE Equity,Atlantic Power Corporation (AT),AT
                    NYSE Equity,Atmos Energy Corporation (ATO),ATO
                    NYSE Equity,AU Optronics Corp (AUO),AUO
                    NYSE Equity,Aurora Cannabis Inc. (ACB),ACB
                    NYSE Equity,Autohome Inc. (ATHM),ATHM
                    NYSE Equity,"Autoliv, Inc. (ALV)",ALV
                    NYSE Equity,"AutoNation, Inc. (AN)",AN
                    NYSE Equity,"AutoZone, Inc. (AZO)",AZO
                    NYSE Equity,"Avalara, Inc. (AVLR)",AVLR
                    NYSE Equity,"AvalonBay Communities, Inc. (AVB)",AVB
                    NYSE Equity,"Avangrid, Inc. (AGR)",AGR
                    NYSE Equity,"Avanos Medical, Inc. (AVNS)",AVNS
                    NYSE Equity,"Avantor, Inc. (AVTR)",AVTR
                    NYSE Equity,"Avantor, Inc. (AVTR^A)",AVTR^A
                    NYSE Equity,Avaya Holdings Corp. (AVYA),AVYA
                    NYSE Equity,Avery Dennison Corporation (AVY),AVY
                    NYSE Equity,Avianca Holdings S.A. (AVH),AVH
                    NYSE Equity,Avista Corporation (AVA),AVA
                    NYSE Equity,"Avon Products, Inc. (AVP)",AVP
                    NYSE Equity,AVX Corporation (AVX),AVX
                    NYSE Equity,"AXA Equitable Holdings, Inc. (EQH)",EQH
                    NYSE Equity,Axalta Coating Systems Ltd. (AXTA),AXTA
                    NYSE Equity,Axis Capital Holdings Limited (AXS),AXS
                    NYSE Equity,Axis Capital Holdings Limited (AXS^D),AXS^D
                    NYSE Equity,Axis Capital Holdings Limited (AXS^E),AXS^E
                    NYSE Equity,"Axos Financial, Inc. (AX)",AX
                    NYSE Equity,"Axos Financial, Inc. (AXO)",AXO
                    NYSE Equity,Azul S.A. (AZUL),AZUL
                    NYSE Equity,Azure Power Global Limited (AZRE),AZRE
                    NYSE Equity,AZZ Inc. (AZZ),AZZ
                    NYSE Equity,"B&G Foods, Inc. (BGS)",BGS
                    NYSE Equity,B. Riley Principal Merger Corp. (BRPM),BRPM
                    NYSE Equity,B. Riley Principal Merger Corp. (BRPM.U),BRPM.U
                    NYSE Equity,B. Riley Principal Merger Corp. (BRPM.WS),BRPM.WS
                    NYSE Equity,Babcock (BW),BW
                    NYSE Equity,Babson Global Short Duration High Yield Fund (BGH),BGH
                    NYSE Equity,"Badger Meter, Inc. (BMI)",BMI
                    NYSE Equity,"Bain Capital Specialty Finance, Inc. (BCSF)",BCSF
                    NYSE Equity,"Baker Hughes, a GE company (BHGE)",BHGE
                    NYSE Equity,BalckRock Taxable Municipal Bond Trust (BBN),BBN
                    NYSE Equity,Ball Corporation (BLL),BLL
                    NYSE Equity,"Banc of California, Inc. (BANC)",BANC
                    NYSE Equity,"Banc of California, Inc. (BANC^D)",BANC^D
                    NYSE Equity,"Banc of California, Inc. (BANC^E)",BANC^E
                    NYSE Equity,Banco Bilbao Viscaya Argentaria S.A. (BBVA),BBVA
                    NYSE Equity,Banco Bradesco Sa (BBD),BBD
                    NYSE Equity,Banco Bradesco Sa (BBDO),BBDO
                    NYSE Equity,Banco De Chile (BCH),BCH
                    NYSE Equity,"Banco Latinoamericano de Comercio Exterior, S.A. (BLX)",BLX
                    NYSE Equity,Banco Santander Brasil SA (BSBR),BSBR
                    NYSE Equity,Banco Santander Chile (BSAC),BSAC
                    NYSE Equity,"Banco Santander Mexico, S.A., Institucion de Ban (BSMX)",BSMX
                    NYSE Equity,"Banco Santander, S.A. (SAN)",SAN
                    NYSE Equity,"Banco Santander, S.A. (SAN^B)",SAN^B
                    NYSE Equity,BanColombia S.A. (CIB),CIB
                    NYSE Equity,BancorpSouth Bank (BXS),BXS
                    NYSE Equity,Bank of America Corporation (BAC),BAC
                    NYSE Equity,Bank of America Corporation (BAC^A),BAC^A
                    NYSE Equity,Bank of America Corporation (BAC^B),BAC^B
                    NYSE Equity,Bank of America Corporation (BAC^C),BAC^C
                    NYSE Equity,Bank of America Corporation (BAC^E),BAC^E
                    NYSE Equity,Bank of America Corporation (BAC^K),BAC^K
                    NYSE Equity,Bank of America Corporation (BAC^L),BAC^L
                    NYSE Equity,Bank of America Corporation (BAC^W),BAC^W
                    NYSE Equity,Bank of America Corporation (BAC^Y),BAC^Y
                    NYSE Equity,Bank of America Corporation (BML^G),BML^G
                    NYSE Equity,Bank of America Corporation (BML^H),BML^H
                    NYSE Equity,Bank of America Corporation (BML^J),BML^J
                    NYSE Equity,Bank of America Corporation (BML^L),BML^L
                    NYSE Equity,Bank of Hawaii Corporation (BOH),BOH
                    NYSE Equity,Bank Of Montreal (BMO),BMO
                    NYSE Equity,Bank of N.T. Butterfield & Son Limited (The) (NTB),NTB
                    NYSE Equity,Bank Of New York Mellon Corporation (The) (BK),BK
                    NYSE Equity,Bank Of New York Mellon Corporation (The) (BK^C),BK^C
                    NYSE Equity,Bank of Nova Scotia (The) (BNS),BNS
                    NYSE Equity,"BankUnited, Inc. (BKU)",BKU
                    NYSE Equity,Barclays PLC (BCS),BCS
                    NYSE Equity,"Barings BDC, Inc. (BBDC)",BBDC
                    NYSE Equity,Barings Corporate Investors (MCI),MCI
                    NYSE Equity,Barings Participation Investors (MPV),MPV
                    NYSE Equity,"Barnes & Noble Education, Inc (BNED)",BNED
                    NYSE Equity,"Barnes & Noble, Inc. (BKS)",BKS
                    NYSE Equity,"Barnes Group, Inc. (B)",B
                    NYSE Equity,Barrick Gold Corporation (GOLD),GOLD
                    NYSE Equity,"Basic Energy Services, Inc. (BAS)",BAS
                    NYSE Equity,Bausch Health Companies Inc. (BHC),BHC
                    NYSE Equity,Baxter International Inc. (BAX),BAX
                    NYSE Equity,Baytex Energy Corp (BTE),BTE
                    NYSE Equity,BB&T Corporation (BBT),BBT
                    NYSE Equity,BB&T Corporation (BBT^D),BBT^D
                    NYSE Equity,BB&T Corporation (BBT^E),BBT^E
                    NYSE Equity,BB&T Corporation (BBT^F),BBT^F
                    NYSE Equity,BB&T Corporation (BBT^G),BBT^G
                    NYSE Equity,BB&T Corporation (BBT^H),BBT^H
                    NYSE Equity,BBVA Banco Frances S.A. (BBAR),BBAR
                    NYSE Equity,BBX Capital Corporation (BBX),BBX
                    NYSE Equity,"BCE, Inc. (BCE)",BCE
                    NYSE Equity,"Beazer Homes USA, Inc. (BZH)",BZH
                    NYSE Equity,"Becton, Dickinson and Company (BDX)",BDX
                    NYSE Equity,"Becton, Dickinson and Company (BDXA)",BDXA
                    NYSE Equity,Belden Inc (BDC),BDC
                    NYSE Equity,Belden Inc (BDC^B),BDC^B
                    NYSE Equity,"Benchmark Electronics, Inc. (BHE)",BHE
                    NYSE Equity,Berkshire Hathaway Inc. (BRK.A),BRK.A
                    NYSE Equity,Berkshire Hathaway Inc. (BRK.B),BRK.B
                    NYSE Equity,"Berkshire Hills Bancorp, Inc. (BHLB)",BHLB
                    NYSE Equity,"Berry Global Group, Inc. (BERY)",BERY
                    NYSE Equity,"Best Buy Co., Inc. (BBY)",BBY
                    NYSE Equity,BEST Inc. (BEST),BEST
                    NYSE Equity,BHP Group Limited (BHP),BHP
                    NYSE Equity,BHP Group Plc (BBL),BBL
                    NYSE Equity,"Big Lots, Inc. (BIG)",BIG
                    NYSE Equity,Biglari Holdings Inc. (BH),BH
                    NYSE Equity,Biglari Holdings Inc. (BH.A),BH.A
                    NYSE Equity,Biohaven Pharmaceutical Holding Company Ltd. (BHVN),BHVN
                    NYSE Equity,"Bio-Rad Laboratories, Inc. (BIO)",BIO
                    NYSE Equity,"Bio-Rad Laboratories, Inc. (BIO.B)",BIO.B
                    NYSE Equity,Bitauto Holdings Limited (BITA),BITA
                    NYSE Equity,"BJ&#39;s Wholesale Club Holdings, Inc. (BJ)",BJ
                    NYSE Equity,Black Hills Corporation (BKH),BKH
                    NYSE Equity,"Black Knight, Inc. (BKI)",BKI
                    NYSE Equity,"Black Stone Minerals, L.P. (BSM)",BSM
                    NYSE Equity,BlackBerry Limited (BB),BB
                    NYSE Equity,BlackRock 2022 Global Income Opportunity Trust (BGIO),BGIO
                    NYSE Equity,BlackRock California Municipal Income Trust (BFZ),BFZ
                    NYSE Equity,Blackrock Capital and Income Strategies Fund Inc (CII),CII
                    NYSE Equity,Blackrock Core Bond Trust (BHK),BHK
                    NYSE Equity,"Blackrock Corporate High Yield Fund, Inc. (HYT)",HYT
                    NYSE Equity,BlackRock Credit Allocation Income Trust (BTZ),BTZ
                    NYSE Equity,"Blackrock Debt Strategies Fund, Inc. (DSU)",DSU
                    NYSE Equity,BlackRock Energy and Resources Trust (BGR),BGR
                    NYSE Equity,Blackrock Enhanced Equity Dividend Trust (BDJ),BDJ
                    NYSE Equity,"Blackrock Enhanced Government Fund, Inc (EGF)",EGF
                    NYSE Equity,Blackrock Floating Rate Income Strategies Fund Inc (FRA),FRA
                    NYSE Equity,Blackrock Florida Municipal 2020 Term Trust (BFO),BFO
                    NYSE Equity,Blackrock Global (BGT),BGT
                    NYSE Equity,Blackrock Global (BOE),BOE
                    NYSE Equity,Blackrock Health Sciences Trust (BME),BME
                    NYSE Equity,BlackRock Income Investment Quality Trust (BAF),BAF
                    NYSE Equity,BlackRock Income Trust Inc. (The) (BKT),BKT
                    NYSE Equity,"BLACKROCK INTERNATIONAL, LTD. (BGY)",BGY
                    NYSE Equity,BlackRock Investment Quality Municipal Trust Inc. (The) (BKN),BKN
                    NYSE Equity,BlackRock Long-Term Municipal Advantage Trust (BTA),BTA
                    NYSE Equity,BlackRock Maryland Municipal Bond Trust (BZM),BZM
                    NYSE Equity,BlackRock Massachusetts Tax-Exempt Trust (MHE),MHE
                    NYSE Equity,BlackRock Multi-Sector Income Trust (BIT),BIT
                    NYSE Equity,Blackrock Muni Intermediate Duration Fund Inc (MUI),MUI
                    NYSE Equity,Blackrock Muni New York Intermediate Duration Fund Inc (MNE),MNE
                    NYSE Equity,"Blackrock MuniAssets Fund, Inc. (MUA)",MUA
                    NYSE Equity,Blackrock Municipal 2020 Term Trust (BKK),BKK
                    NYSE Equity,Blackrock Municipal Bond Trust (BBK),BBK
                    NYSE Equity,BlackRock Municipal Income Investment Trust (BBF),BBF
                    NYSE Equity,Blackrock Municipal Income Quality Trust (BYM),BYM
                    NYSE Equity,BlackRock Municipal Income Trust (BFK),BFK
                    NYSE Equity,BlackRock Municipal Income Trust II (BLE),BLE
                    NYSE Equity,BlackRock Municipal Target Term Trust Inc. (The) (BTT),BTT
                    NYSE Equity,"Blackrock MuniEnhanced Fund, Inc. (MEN)",MEN
                    NYSE Equity,"Blackrock MuniHoldings California Quality Fund,  Inc. (MUC)",MUC
                    NYSE Equity,"Blackrock MuniHoldings Fund II, Inc. (MUH)",MUH
                    NYSE Equity,"Blackrock MuniHoldings Fund, Inc. (MHD)",MHD
                    NYSE Equity,Blackrock MuniHoldings Investment Quality Fund (MFL),MFL
                    NYSE Equity,"Blackrock MuniHoldings New Jersey Insured Fund, Inc. (MUJ)",MUJ
                    NYSE Equity,"Blackrock MuniHoldings New York Quality Fund, Inc. (MHN)",MHN
                    NYSE Equity,"Blackrock MuniHoldings Quality Fund II, Inc. (MUE)",MUE
                    NYSE Equity,"Blackrock MuniHoldings Quality Fund, Inc. (MUS)",MUS
                    NYSE Equity,"Blackrock MuniVest Fund II, Inc. (MVT)",MVT
                    NYSE Equity,"Blackrock MuniYield California Fund, Inc. (MYC)",MYC
                    NYSE Equity,"Blackrock MuniYield California Insured Fund, Inc. (MCA)",MCA
                    NYSE Equity,"Blackrock MuniYield Fund, Inc. (MYD)",MYD
                    NYSE Equity,Blackrock MuniYield Investment Fund (MYF),MYF
                    NYSE Equity,Blackrock MuniYield Investment QualityFund (MFT),MFT
                    NYSE Equity,"Blackrock MuniYield Michigan Quality Fund, Inc. (MIY)",MIY
                    NYSE Equity,"Blackrock MuniYield New Jersey Fund, Inc. (MYJ)",MYJ
                    NYSE Equity,"Blackrock MuniYield New York Quality Fund, Inc. (MYN)",MYN
                    NYSE Equity,Blackrock MuniYield Pennsylvania Quality Fund (MPA),MPA
                    NYSE Equity,"Blackrock MuniYield Quality Fund II, Inc. (MQT)",MQT
                    NYSE Equity,"Blackrock MuniYield Quality Fund III, Inc. (MYI)",MYI
                    NYSE Equity,"Blackrock MuniYield Quality Fund, Inc. (MQY)",MQY
                    NYSE Equity,BlackRock New York Investment Quality Municipal Trust Inc. (Th (BNY),BNY
                    NYSE Equity,Blackrock New York Municipal Bond Trust (BQH),BQH
                    NYSE Equity,Blackrock New York Municipal Income Quality Trust (BSE),BSE
                    NYSE Equity,BlackRock New York Municipal Income Trust II (BFY),BFY
                    NYSE Equity,BlackRock Resources (BCX),BCX
                    NYSE Equity,BlackRock Science and Technology Trust (BST),BST
                    NYSE Equity,BlackRock Strategic Municipal Trust Inc. (The) (BSD),BSD
                    NYSE Equity,"BlackRock Utility, Infrastructure & Power Opportun (BUI)",BUI
                    NYSE Equity,BlackRock Virginia Municipal Bond Trust (BHV),BHV
                    NYSE Equity,"BlackRock, Inc. (BLK)",BLK
                    NYSE Equity,Blackstone / GSO Strategic Credit Fund (BGB),BGB
                    NYSE Equity,Blackstone GSO Long Short Credit Income Fund (BGX),BGX
                    NYSE Equity,Blackstone GSO Senior Floating Rate Term Fund (BSL),BSL
                    NYSE Equity,Bloom Energy Corporation (BE),BE
                    NYSE Equity,"Blue Apron Holdings, Inc. (APRN)",APRN
                    NYSE Equity,Blue Capital Reinsurance Holdings Ltd. (BCRH),BCRH
                    NYSE Equity,Bluegreen Vacations Corporation (BXG),BXG
                    NYSE Equity,BlueLinx Holdings Inc. (BXC),BXC
                    NYSE Equity,BNY Mellon Alcentra Global Credit Income 2024 Target Term Fund (DCF),DCF
                    NYSE Equity,BNY Mellon High Yield Strategies Fund (DHF),DHF
                    NYSE Equity,"BNY Mellon Municipal Bond Infrastructure Fund, Inc (DMB)",DMB
                    NYSE Equity,"BNY Mellon Strategic Municipal Bond Fund, Inc. (DSM)",DSM
                    NYSE Equity,"BNY Mellon Strategic Municipals, Inc. (LEO)",LEO
                    NYSE Equity,Boeing Company (The) (BA),BA
                    NYSE Equity,"Boise Cascade, L.L.C. (BCC)",BCC
                    NYSE Equity,"Bonanza Creek Energy, Inc. (BCEI)",BCEI
                    NYSE Equity,"Boot Barn Holdings, Inc. (BOOT)",BOOT
                    NYSE Equity,Booz Allen Hamilton Holding Corporation (BAH),BAH
                    NYSE Equity,BorgWarner Inc. (BWA),BWA
                    NYSE Equity,"Boston Beer Company, Inc. (The) (SAM)",SAM
                    NYSE Equity,"Boston Properties, Inc. (BXP)",BXP
                    NYSE Equity,"Boston Properties, Inc. (BXP^B)",BXP^B
                    NYSE Equity,Boston Scientific Corporation (BSX),BSX
                    NYSE Equity,"Box, Inc. (BOX)",BOX
                    NYSE Equity,Boyd Gaming Corporation (BYD),BYD
                    NYSE Equity,BP Midstream Partners LP (BPMP),BPMP
                    NYSE Equity,BP p.l.c. (BP),BP
                    NYSE Equity,BP Prudhoe Bay Royalty Trust (BPT),BPT
                    NYSE Equity,Brady Corporation (BRC),BRC
                    NYSE Equity,Braemar Hotels & Resorts Inc. (BHR),BHR
                    NYSE Equity,Braemar Hotels & Resorts Inc. (BHR^B),BHR^B
                    NYSE Equity,Braemar Hotels & Resorts Inc. (BHR^D),BHR^D
                    NYSE Equity,Brandywine Realty Trust (BDN),BDN
                    NYSE Equity,BrandywineGLOBAL Global Income Opportunities Fund  (BWG),BWG
                    NYSE Equity,Brasilagro Cia Brasileira De Propriedades Agricolas (LND),LND
                    NYSE Equity,BRF S.A. (BRFS),BRFS
                    NYSE Equity,Briggs & Stratton Corporation (BGG),BGG
                    NYSE Equity,"Brigham Minerals, Inc. (MNRL)",MNRL
                    NYSE Equity,Bright Horizons Family Solutions Inc. (BFAM),BFAM
                    NYSE Equity,Bright Scholar Education Holdings Limited (BEDU),BEDU
                    NYSE Equity,BrightSphere Investment Group plc (BSA),BSA
                    NYSE Equity,BrightSphere Investment Group plc (BSIG),BSIG
                    NYSE Equity,"BrightView Holdings, Inc. (BV)",BV
                    NYSE Equity,"Brinker International, Inc. (EAT)",EAT
                    NYSE Equity,Brink&#39;s Company (The) (BCO),BCO
                    NYSE Equity,Bristol-Myers Squibb Company (BMY),BMY
                    NYSE Equity,British American Tobacco p.l.c. (BTI),BTI
                    NYSE Equity,Brixmor Property Group Inc. (BRX),BRX
                    NYSE Equity,"Broadridge Financial Solutions, Inc. (BR)",BR
                    NYSE Equity,Brookdale Senior Living Inc. (BKD),BKD
                    NYSE Equity,Brookfield Asset Management Inc (BAM),BAM
                    NYSE Equity,Brookfield Business Partners L.P. (BBU),BBU
                    NYSE Equity,Brookfield DTLA Inc. (DTLA^),DTLA^
                    NYSE Equity,Brookfield Global Listed Infrastructure Income Fund (INF),INF
                    NYSE Equity,Brookfield Infrastructure Partners LP (BIP),BIP
                    NYSE Equity,Brookfield Real Assets Income Fund Inc. (RA),RA
                    NYSE Equity,Brookfield Renewable Partners L.P. (BEP),BEP
                    NYSE Equity,"Brown & Brown, Inc. (BRO)",BRO
                    NYSE Equity,Brown Forman Corporation (BF.A),BF.A
                    NYSE Equity,Brown Forman Corporation (BF.B),BF.B
                    NYSE Equity,BRT Apartments Corp. (BRT),BRT
                    NYSE Equity,Brunswick Corporation (BC),BC
                    NYSE Equity,Brunswick Corporation (BC^A),BC^A
                    NYSE Equity,Brunswick Corporation (BC^B),BC^B
                    NYSE Equity,Brunswick Corporation (BC^C),BC^C
                    NYSE Equity,BT Group plc (BT),BT
                    NYSE Equity,Buckeye Partners L.P. (BPL),BPL
                    NYSE Equity,"Buckle, Inc. (The) (BKE)",BKE
                    NYSE Equity,Buenaventura Mining Company Inc. (BVN),BVN
                    NYSE Equity,"Build-A-Bear Workshop, Inc. (BBW)",BBW
                    NYSE Equity,Bunge Limited (BG),BG
                    NYSE Equity,"Burlington Stores, Inc. (BURL)",BURL
                    NYSE Equity,"BWX Technologies, Inc. (BWXT)",BWXT
                    NYSE Equity,"Byline Bancorp, Inc. (BY)",BY
                    NYSE Equity,"C&J Energy Services, Inc (CJ)",CJ
                    NYSE Equity,CABCO Series 2004-101 Trust (GYB),GYB
                    NYSE Equity,CABCO Series 2004-101 Trust (PFH),PFH
                    NYSE Equity,"Cable One, Inc. (CABO)",CABO
                    NYSE Equity,Cabot Corporation (CBT),CBT
                    NYSE Equity,Cabot Oil & Gas Corporation (COG),COG
                    NYSE Equity,"CACI International, Inc. (CACI)",CACI
                    NYSE Equity,"Cactus, Inc. (WHD)",WHD
                    NYSE Equity,Cadence Bancorporation (CADE),CADE
                    NYSE Equity,CAE Inc (CAE),CAE
                    NYSE Equity,"CAI International, Inc. (CAI)",CAI
                    NYSE Equity,"CAI International, Inc. (CAI^A)",CAI^A
                    NYSE Equity,"CAI International, Inc. (CAI^B)",CAI^B
                    NYSE Equity,"Caleres, Inc. (CAL)",CAL
                    NYSE Equity,California Resources Corporation (CRC),CRC
                    NYSE Equity,California Water  Service Group Holding (CWT),CWT
                    NYSE Equity,"Calix, Inc (CALX)",CALX
                    NYSE Equity,Callaway Golf Company (ELY),ELY
                    NYSE Equity,Callon Petroleum Company (CPE),CPE
                    NYSE Equity,Callon Petroleum Company (CPE^A.CL),CPE^A.CL
                    NYSE Equity,Cambrex Corporation (CBM),CBM
                    NYSE Equity,Camden Property Trust (CPT),CPT
                    NYSE Equity,Cameco Corporation (CCJ),CCJ
                    NYSE Equity,Campbell Soup Company (CPB),CPB
                    NYSE Equity,"Camping World Holdings, Inc. (CWH)",CWH
                    NYSE Equity,Canada Goose Holdings Inc. (GOOS),GOOS
                    NYSE Equity,Canadian Imperial Bank of Commerce (CM),CM
                    NYSE Equity,Canadian National Railway Company (CNI),CNI
                    NYSE Equity,Canadian Natural Resources Limited (CNQ),CNQ
                    NYSE Equity,Canadian Pacific Railway Limited (CP),CP
                    NYSE Equity,Cango Inc. (CANG),CANG
                    NYSE Equity,"Cannae Holdings, Inc. (CNNE)",CNNE
                    NYSE Equity,CannTrust Holdings Inc. (CTST),CTST
                    NYSE Equity,"Canon, Inc. (CAJ)",CAJ
                    NYSE Equity,Canopy Growth Corporation (CGC),CGC
                    NYSE Equity,Cantel Medical Corp. (CMD),CMD
                    NYSE Equity,Capital One Financial Corporation (COF),COF
                    NYSE Equity,Capital One Financial Corporation (COF^C),COF^C
                    NYSE Equity,Capital One Financial Corporation (COF^D),COF^D
                    NYSE Equity,Capital One Financial Corporation (COF^F),COF^F
                    NYSE Equity,Capital One Financial Corporation (COF^G),COF^G
                    NYSE Equity,Capital One Financial Corporation (COF^H),COF^H
                    NYSE Equity,Capital One Financial Corporation (COF^P),COF^P
                    NYSE Equity,Capital Senior Living Corporation (CSU),CSU
                    NYSE Equity,"Capital Trust, Inc. (BXMT)",BXMT
                    NYSE Equity,Capitol Investment Corp. IV (CIC),CIC
                    NYSE Equity,Capitol Investment Corp. IV (CIC.U),CIC.U
                    NYSE Equity,Capitol Investment Corp. IV (CIC.WS),CIC.WS
                    NYSE Equity,Capri Holdings Limited (CPRI),CPRI
                    NYSE Equity,Capstead Mortgage Corporation (CMO),CMO
                    NYSE Equity,Capstead Mortgage Corporation (CMO^E),CMO^E
                    NYSE Equity,"Carbo Ceramics, Inc. (CRR)",CRR
                    NYSE Equity,"Cardinal Health, Inc. (CAH)",CAH
                    NYSE Equity,"Care.com, Inc. (CRCM)",CRCM
                    NYSE Equity,Carlisle Companies Incorporated (CSL),CSL
                    NYSE Equity,CarMax Inc (KMX),KMX
                    NYSE Equity,Carnival Corporation (CCL),CCL
                    NYSE Equity,Carnival Corporation (CUK),CUK
                    NYSE Equity,Carpenter Technology Corporation (CRS),CRS
                    NYSE Equity,"Carriage Services, Inc. (CSV)",CSV
                    NYSE Equity,Cars.com Inc. (CARS),CARS
                    NYSE Equity,"Carter&#39;s, Inc. (CRI)",CRI
                    NYSE Equity,Carvana Co. (CVNA),CVNA
                    NYSE Equity,"Castlight Health, inc. (CSLT)",CSLT
                    NYSE Equity,"Catalent, Inc. (CTLT)",CTLT
                    NYSE Equity,"CatchMark Timber Trust, Inc. (CTT           )",CTT           
                    NYSE Equity,"Caterpillar, Inc. (CAT)",CAT
                    NYSE Equity,Cato Corporation (The) (CATO),CATO
                    NYSE Equity,"CBIZ, Inc. (CBZ)",CBZ
                    NYSE Equity,"CBL & Associates Properties, Inc. (CBL)",CBL
                    NYSE Equity,"CBL & Associates Properties, Inc. (CBL^D)",CBL^D
                    NYSE Equity,"CBL & Associates Properties, Inc. (CBL^E)",CBL^E
                    NYSE Equity,CBO (Listing Market - NYSE - Networks A/E) (CBO),CBO
                    NYSE Equity,CBRE Clarion Global Real Estate Income Fund (IGR),IGR
                    NYSE Equity,"CBRE Group, Inc. (CBRE)",CBRE
                    NYSE Equity,CBS Corporation (CBS),CBS
                    NYSE Equity,CBS Corporation (CBS.A),CBS.A
                    NYSE Equity,CBX (Listing Market NYSE Networks AE (CBX),CBX
                    NYSE Equity,"Cedar Fair, L.P. (FUN)",FUN
                    NYSE Equity,"Cedar Realty Trust, Inc. (CDR)",CDR
                    NYSE Equity,"Cedar Realty Trust, Inc. (CDR^B)",CDR^B
                    NYSE Equity,"Cedar Realty Trust, Inc. (CDR^C)",CDR^C
                    NYSE Equity,Celanese Corporation (CE),CE
                    NYSE Equity,"Celestica, Inc. (CLS)",CLS
                    NYSE Equity,"Cellcom Israel, Ltd. (CEL)",CEL
                    NYSE Equity,Cementos Pacasmayo S.A.A. (CPAC),CPAC
                    NYSE Equity,Cemex S.A.B. de C.V. (CX),CX
                    NYSE Equity,Cenovus Energy Inc (CVE),CVE
                    NYSE Equity,Centene Corporation (CNC),CNC
                    NYSE Equity,Center Coast Brookfield MLP & Energy Infrastructur (CEN),CEN
                    NYSE Equity,"CenterPoint Energy, Inc. (CNP)",CNP
                    NYSE Equity,"CenterPoint Energy, Inc. (CNP^B)",CNP^B
                    NYSE Equity,Centrais Electricas Brasileiras S.A.- Eletrobras (EBR),EBR
                    NYSE Equity,Centrais Electricas Brasileiras S.A.- Eletrobras (EBR.B),EBR.B
                    NYSE Equity,Central Puerto S.A. (CEPU),CEPU
                    NYSE Equity,"Century Communities, Inc. (CCS)",CCS
                    NYSE Equity,"CenturyLink, Inc. (CTL)",CTL
                    NYSE Equity,Ceridian HCM Holding Inc. (CDAY),CDAY
                    NYSE Equity,"CF Industries Holdings, Inc. (CF)",CF
                    NYSE Equity,CGI Inc. (GIB),GIB
                    NYSE Equity,ChannelAdvisor Corporation (ECOM          ),ECOM          
                    NYSE Equity,"Chaparral Energy, Inc. (CHAP)",CHAP
                    NYSE Equity,"Charah Solutions, Inc. (CHRA)",CHRA
                    NYSE Equity,"Charles River Laboratories International, Inc. (CRL)",CRL
                    NYSE Equity,Chatham Lodging Trust (REIT) (CLDT),CLDT
                    NYSE Equity,Cheetah Mobile Inc. (CMCM),CMCM
                    NYSE Equity,"Chegg, Inc. (CHGG)",CHGG
                    NYSE Equity,Chemed Corp. (CHE),CHE
                    NYSE Equity,Chemours Company (The) (CC),CC
                    NYSE Equity,Cherry Hill Mortgage Investment Corporation (CHMI),CHMI
                    NYSE Equity,Cherry Hill Mortgage Investment Corporation (CHMI^A),CHMI^A
                    NYSE Equity,Cherry Hill Mortgage Investment Corporation (CHMI^B),CHMI^B
                    NYSE Equity,Chesapeake Energy Corporation (CHK),CHK
                    NYSE Equity,Chesapeake Energy Corporation (CHK^D),CHK^D
                    NYSE Equity,Chesapeake Granite Wash Trust (CHKR),CHKR
                    NYSE Equity,Chesapeake Lodging Trust (CHSP),CHSP
                    NYSE Equity,Chesapeake Utilities Corporation (CPK),CPK
                    NYSE Equity,Chevron Corporation (CVX),CVX
                    NYSE Equity,"Chewy, Inc. (CHWY)",CHWY
                    NYSE Equity,"Chico&#39;s FAS, Inc. (CHS)",CHS
                    NYSE Equity,Chimera Investment Corporation (CIM),CIM
                    NYSE Equity,Chimera Investment Corporation (CIM^A),CIM^A
                    NYSE Equity,Chimera Investment Corporation (CIM^B),CIM^B
                    NYSE Equity,Chimera Investment Corporation (CIM^C),CIM^C
                    NYSE Equity,Chimera Investment Corporation (CIM^D),CIM^D
                    NYSE Equity,China Distance Education Holdings Limited (DL),DL
                    NYSE Equity,China Eastern Airlines Corporation Ltd. (CEA),CEA
                    NYSE Equity,"China Fund, Inc. (The) (CHN)",CHN
                    NYSE Equity,"China Green Agriculture, Inc. (CGA)",CGA
                    NYSE Equity,China Life Insurance Company Limited (LFC),LFC
                    NYSE Equity,China Mobile (Hong Kong) Ltd. (CHL),CHL
                    NYSE Equity,China Online Education Group (COE),COE
                    NYSE Equity,China Petroleum & Chemical Corporation (SNP),SNP
                    NYSE Equity,China Rapid Finance Limited (XRF),XRF
                    NYSE Equity,China Southern Airlines Company Limited (ZNH),ZNH
                    NYSE Equity,China Telecom Corp Ltd (CHA),CHA
                    NYSE Equity,China Unicom (Hong Kong) Ltd (CHU),CHU
                    NYSE Equity,China Yuchai International Limited (CYD),CYD
                    NYSE Equity,"Chipotle Mexican Grill, Inc. (CMG)",CMG
                    NYSE Equity,"Choice Hotels International, Inc. (CHH)",CHH
                    NYSE Equity,Chubb Limited (CB),CB
                    NYSE Equity,"Chunghwa Telecom Co., Ltd. (CHT)",CHT
                    NYSE Equity,"Church & Dwight Company, Inc. (CHD)",CHD
                    NYSE Equity,Ciena Corporation (CIEN),CIEN
                    NYSE Equity,Cigna Corporation (CI),CI
                    NYSE Equity,Cimarex Energy Co (XEC),XEC
                    NYSE Equity,Cincinnati Bell Inc (CBB),CBB
                    NYSE Equity,Cincinnati Bell Inc (CBB^B),CBB^B
                    NYSE Equity,Cinemark Holdings Inc (CNK),CNK
                    NYSE Equity,Ciner Resources LP (CINR),CINR
                    NYSE Equity,"CIRCOR International, Inc. (CIR)",CIR
                    NYSE Equity,Cision Ltd. (CISN),CISN
                    NYSE Equity,CIT Group Inc (DEL) (CIT),CIT
                    NYSE Equity,Citigroup Inc. (BLW),BLW
                    NYSE Equity,Citigroup Inc. (C),C
                    NYSE Equity,Citigroup Inc. (C^J),C^J
                    NYSE Equity,Citigroup Inc. (C^K),C^K
                    NYSE Equity,Citigroup Inc. (C^N),C^N
                    NYSE Equity,Citigroup Inc. (C^S),C^S
                    NYSE Equity,"Citizens Financial Group, Inc. (CFG)",CFG
                    NYSE Equity,"Citizens Financial Group, Inc. (CFG^D)",CFG^D
                    NYSE Equity,"Citizens, Inc. (CIA)",CIA
                    NYSE Equity,"City Office REIT, Inc. (CIO)",CIO
                    NYSE Equity,"City Office REIT, Inc. (CIO^A)",CIO^A
                    NYSE Equity,Civeo Corporation (CVEO),CVEO
                    NYSE Equity,Clarivate Analytics Plc (CCC),CCC
                    NYSE Equity,"Clean Harbors, Inc. (CLH)",CLH
                    NYSE Equity,"Clear Channel Outdoor Holdings, Inc. (CCO)",CCO
                    NYSE Equity,ClearBridge Energy Midstream Opportunity Fund Inc. (EMO),EMO
                    NYSE Equity,ClearBridge MLP and Midstream Fund Inc. (CEM),CEM
                    NYSE Equity,ClearBridge MLP and Midstream Total Return Fund In (CTR),CTR
                    NYSE Equity,Clearwater Paper Corporation (CLW),CLW
                    NYSE Equity,"Clearway Energy, Inc. (CWEN)",CWEN
                    NYSE Equity,"Clearway Energy, Inc. (CWEN.A)",CWEN.A
                    NYSE Equity,Cleveland-Cliffs Inc. (CLF),CLF
                    NYSE Equity,Clipper Realty Inc. (CLPR),CLPR
                    NYSE Equity,Clorox Company (The) (CLX),CLX
                    NYSE Equity,"Cloudera, Inc. (CLDR)",CLDR
                    NYSE Equity,CMS Energy Corporation (CMS),CMS
                    NYSE Equity,CMS Energy Corporation (CMS^B),CMS^B
                    NYSE Equity,CMS Energy Corporation (CMSA),CMSA
                    NYSE Equity,CMS Energy Corporation (CMSC),CMSC
                    NYSE Equity,CMS Energy Corporation (CMSD),CMSD
                    NYSE Equity,CNA Financial Corporation (CNA),CNA
                    NYSE Equity,CNFinance Holdings Limited (CNF),CNF
                    NYSE Equity,CNH Industrial N.V. (CNHI),CNHI
                    NYSE Equity,"CNO Financial Group, Inc. (CNO)",CNO
                    NYSE Equity,CNOOC Limited (CEO),CEO
                    NYSE Equity,CNX Midstream Partners LP (CNXM),CNXM
                    NYSE Equity,CNX Resources Corporation (CEIX),CEIX
                    NYSE Equity,CNX Resources Corporation (CNX),CNX
                    NYSE Equity,Coca Cola Femsa S.A.B. de C.V. (KOF),KOF
                    NYSE Equity,Coca-Cola Company (The) (KO),KO
                    NYSE Equity,Coca-Cola European Partners plc (CCEP),CCEP
                    NYSE Equity,"Coeur Mining, Inc. (CDE)",CDE
                    NYSE Equity,"Cohen & Steers Closed-End Opportunity Fund, Inc. (FOF)",FOF
                    NYSE Equity,"Cohen & Steers Global Income Builder, Inc. (INB)",INB
                    NYSE Equity,Cohen & Steers Inc (CNS),CNS
                    NYSE Equity,"Cohen & Steers Infrastructure Fund, Inc (UTF)",UTF
                    NYSE Equity,"Cohen & Steers Limited Duration Preferred and Income Fund, Inc (LDP)",LDP
                    NYSE Equity,"Cohen & Steers MLP Income and Energy Opportunity Fund, Inc. (MIE)",MIE
                    NYSE Equity,Cohen & Steers Quality Income Realty Fund Inc (RQI),RQI
                    NYSE Equity,"Cohen & Steers REIT and Preferred and Income Fund, (RNP)",RNP
                    NYSE Equity,"Cohen & Steers Select Preferred and Income Fund, Inc. (PSF)",PSF
                    NYSE Equity,"Cohen & Steers Total Return Realty Fund, Inc. (RFI)",RFI
                    NYSE Equity,Colfax Corporation (CFX),CFX
                    NYSE Equity,Colfax Corporation (CFXA),CFXA
                    NYSE Equity,Colgate-Palmolive Company (CL),CL
                    NYSE Equity,Collier Creek Holdings (CCH),CCH
                    NYSE Equity,Collier Creek Holdings (CCH.U),CCH.U
                    NYSE Equity,Collier Creek Holdings (CCH.WS),CCH.WS
                    NYSE Equity,Colonial High Income Municipal Trust (CXE),CXE
                    NYSE Equity,Colonial Intermediate High Income Fund (CIF),CIF
                    NYSE Equity,Colonial Investment Grade Municipal Trust (CXH),CXH
                    NYSE Equity,Colonial Municipal Income Trust (CMU),CMU
                    NYSE Equity,"Colony Capital, Inc. (CLNY)",CLNY
                    NYSE Equity,"Colony Capital, Inc. (CLNY^B)",CLNY^B
                    NYSE Equity,"Colony Capital, Inc. (CLNY^E)",CLNY^E
                    NYSE Equity,"Colony Capital, Inc. (CLNY^G)",CLNY^G
                    NYSE Equity,"Colony Capital, Inc. (CLNY^H)",CLNY^H
                    NYSE Equity,"Colony Capital, Inc. (CLNY^I)",CLNY^I
                    NYSE Equity,"Colony Capital, Inc. (CLNY^J)",CLNY^J
                    NYSE Equity,"Colony Credit Real Estate, Inc. (CLNC)",CLNC
                    NYSE Equity,"Columbia Property Trust, Inc. (CXP)",CXP
                    NYSE Equity,"Columbia Seligman Premium Technology Growth Fund, Inc (STK)",STK
                    NYSE Equity,Comcast Corporation (CCZ),CCZ
                    NYSE Equity,Comerica Incorporated (CMA),CMA
                    NYSE Equity,"Comfort Systems USA, Inc. (FIX)",FIX
                    NYSE Equity,Commercial Metals Company (CMC),CMC
                    NYSE Equity,"Community Bank System, Inc. (CBU)",CBU
                    NYSE Equity,"Community Health Systems, Inc. (CYH)",CYH
                    NYSE Equity,Community Healthcare Trust Incorporated (CHCT),CHCT
                    NYSE Equity,Comp En De Mn Cemig ADS (CIG),CIG
                    NYSE Equity,Comp En De Mn Cemig ADS (CIG.C),CIG.C
                    NYSE Equity,Companhia Brasileira de Distribuicao (CBD),CBD
                    NYSE Equity,Companhia de saneamento Basico Do Estado De Sao Paulo - Sabesp (SBS),SBS
                    NYSE Equity,Companhia Paranaense de Energia (COPEL) (ELP),ELP
                    NYSE Equity,"Compania Cervecerias Unidas, S.A. (CCU)",CCU
                    NYSE Equity,Compass Diversified Holdings (CODI),CODI
                    NYSE Equity,Compass Diversified Holdings (CODI^A),CODI^A
                    NYSE Equity,Compass Diversified Holdings (CODI^B),CODI^B
                    NYSE Equity,"Compass Minerals International, Inc. (CMP)",CMP
                    NYSE Equity,"Comstock Resources, Inc. (CRK)",CRK
                    NYSE Equity,"ConAgra Brands, Inc. (CAG)",CAG
                    NYSE Equity,Concho Resources Inc. (CXO),CXO
                    NYSE Equity,Concord Medical Services Holdings Limited (CCM),CCM
                    NYSE Equity,Conduent Incorporated (CNDT),CNDT
                    NYSE Equity,ConocoPhillips (COP),COP
                    NYSE Equity,CONSOL Coal Resources LP (CCR),CCR
                    NYSE Equity,Consolidated Edison Inc (ED),ED
                    NYSE Equity,Constellation Brands Inc (STZ),STZ
                    NYSE Equity,Constellation Brands Inc (STZ.B),STZ.B
                    NYSE Equity,Constellium N.V. (CSTM),CSTM
                    NYSE Equity,Container Store (The) (TCS),TCS
                    NYSE Equity,"Continental Building Products, Inc. (CBPX)",CBPX
                    NYSE Equity,"Continental Resources, Inc. (CLR)",CLR
                    NYSE Equity,"Controladora Vuela Compania de Aviacion, S.A.B. de C.V. (VLRS)",VLRS
                    NYSE Equity,"Contura Energy, Inc. (CTRA)",CTRA
                    NYSE Equity,Cooper Tire & Rubber Company (CTB),CTB
                    NYSE Equity,Cooper-Standard Holdings Inc. (CPS),CPS
                    NYSE Equity,CooTek (Cayman) Inc. (CTK),CTK
                    NYSE Equity,"Copa Holdings, S.A. (CPA)",CPA
                    NYSE Equity,Core Laboratories N.V. (CLB),CLB
                    NYSE Equity,"CoreCivic, Inc. (CXW)",CXW
                    NYSE Equity,"CoreLogic, Inc. (CLGX)",CLGX
                    NYSE Equity,"CorEnergy Infrastructure Trust, Inc. (CORR)",CORR
                    NYSE Equity,"CorEnergy Infrastructure Trust, Inc. (CORR^A)",CORR^A
                    NYSE Equity,CorePoint Lodging Inc. (CPLG),CPLG
                    NYSE Equity,CoreSite Realty Corporation (COR),COR
                    NYSE Equity,"Cornerstone Building Brands, Inc. (CNR)",CNR
                    NYSE Equity,Corning Incorporated (GLW),GLW
                    NYSE Equity,Corporacion America Airports SA (CAAP),CAAP
                    NYSE Equity,Corporate Asset Backed Corp CABCO (GYC),GYC
                    NYSE Equity,Corporate Office Properties Trust (OFC),OFC
                    NYSE Equity,"Corteva, Inc. (CTVA)",CTVA
                    NYSE Equity,Cosan Limited (CZZ),CZZ
                    NYSE Equity,Costamare Inc. (CMRE),CMRE
                    NYSE Equity,Costamare Inc. (CMRE^B),CMRE^B
                    NYSE Equity,Costamare Inc. (CMRE^C),CMRE^C
                    NYSE Equity,Costamare Inc. (CMRE^D),CMRE^D
                    NYSE Equity,Costamare Inc. (CMRE^E),CMRE^E
                    NYSE Equity,Cott Corporation (COT),COT
                    NYSE Equity,Coty Inc. (COTY),COTY
                    NYSE Equity,Cousins Properties Incorporated (CUZ),CUZ
                    NYSE Equity,Covanta Holding Corporation (CVA),CVA
                    NYSE Equity,Covia Holdings Corporation (CVIA),CVIA
                    NYSE Equity,CPB Inc. (CPF),CPF
                    NYSE Equity,CPFL Energia S.A. (CPL),CPL
                    NYSE Equity,Crane Co. (CR),CR
                    NYSE Equity,Crawford & Company (CRD.A),CRD.A
                    NYSE Equity,Crawford & Company (CRD.B),CRD.B
                    NYSE Equity,Credicorp Ltd. (BAP),BAP
                    NYSE Equity,Credit Suisse Group (CS),CS
                    NYSE Equity,Crescent Point Energy Corporation (CPG),CPG
                    NYSE Equity,Crestwood Equity Partners LP (CEQP),CEQP
                    NYSE Equity,CRH PLC (CRH),CRH
                    NYSE Equity,Cross Timbers Royalty Trust (CRT),CRT
                    NYSE Equity,CrossAmerica Partners LP (CAPL),CAPL
                    NYSE Equity,Crown Castle International Corporation (CCI),CCI
                    NYSE Equity,Crown Castle International Corporation (CCI^A),CCI^A
                    NYSE Equity,"Crown Holdings, Inc. (CCK)",CCK
                    NYSE Equity,"CryoLife, Inc. (CRY)",CRY
                    NYSE Equity,"CSS Industries, Inc. (CSS)",CSS
                    NYSE Equity,CTS Corporation (CTS),CTS
                    NYSE Equity,CubeSmart (CUBE),CUBE
                    NYSE Equity,Cubic Corporation (CUB),CUB
                    NYSE Equity,"Cullen/Frost Bankers, Inc. (CFR)",CFR
                    NYSE Equity,"Cullen/Frost Bankers, Inc. (CFR^A)",CFR^A
                    NYSE Equity,"Culp, Inc. (CULP)",CULP
                    NYSE Equity,Cummins Inc. (CMI),CMI
                    NYSE Equity,CURO Group Holdings Corp. (CURO),CURO
                    NYSE Equity,Curtiss-Wright Corporation (CW),CW
                    NYSE Equity,Cushing Energy Income Fund (The) (SRF),SRF
                    NYSE Equity,Cushing MLP & Infrastructure Total Return Fund (SRV),SRV
                    NYSE Equity,Cushing Renaissance Fund (The) (SZC),SZC
                    NYSE Equity,Cushing Renaissance Fund (The) (SZC~),SZC~
                    NYSE Equity,Cushman & Wakefield plc (CWK),CWK
                    NYSE Equity,"Customers Bancorp, Inc (CUBI)",CUBI
                    NYSE Equity,"Customers Bancorp, Inc (CUBI^C)",CUBI^C
                    NYSE Equity,"Customers Bancorp, Inc (CUBI^D)",CUBI^D
                    NYSE Equity,"Customers Bancorp, Inc (CUBI^E)",CUBI^E
                    NYSE Equity,"Customers Bancorp, Inc (CUBI^F)",CUBI^F
                    NYSE Equity,CVR Energy Inc. (CVI),CVI
                    NYSE Equity,"CVR Partners, LP (UAN)",UAN
                    NYSE Equity,CVS Health Corporation (CVS),CVS
                    NYSE Equity,"Cypress Energy Partners, L.P. (CELP)",CELP
                    NYSE Equity,"D.R. Horton, Inc. (DHI)",DHI
                    NYSE Equity,Dana Incorporated (DAN),DAN
                    NYSE Equity,Danaher Corporation (DHR),DHR
                    NYSE Equity,Danaher Corporation (DHR^A),DHR^A
                    NYSE Equity,Danaos Corporation (DAC),DAC
                    NYSE Equity,DAQO New Energy Corp. (DQ),DQ
                    NYSE Equity,"Darden Restaurants, Inc. (DRI)",DRI
                    NYSE Equity,Darling Ingredients Inc. (DAR),DAR
                    NYSE Equity,DaVita Inc. (DVA),DVA
                    NYSE Equity,DCP Midstream LP (DCP),DCP
                    NYSE Equity,DCP Midstream LP (DCP^B),DCP^B
                    NYSE Equity,DCP Midstream LP (DCP^C),DCP^C
                    NYSE Equity,Dean Foods Company (DF),DF
                    NYSE Equity,Deckers Outdoor Corporation (DECK),DECK
                    NYSE Equity,Deere & Company (DE),DE
                    NYSE Equity,Delaware Enhanced Global Dividend (DEX),DEX
                    NYSE Equity,"Delaware Investments Dividend & Income Fund, Inc. (DDF)",DDF
                    NYSE Equity,"Delek Logistics Partners, L.P. (DKL)",DKL
                    NYSE Equity,"Delek US Holdings, Inc. (DK)",DK
                    NYSE Equity,Dell Technologies Inc. (DELL),DELL
                    NYSE Equity,Delphi Technologies PLC (DLPH),DLPH
                    NYSE Equity,"Delta Air Lines, Inc. (DAL)",DAL
                    NYSE Equity,Deluxe Corporation (DLX),DLX
                    NYSE Equity,Denbury Resources Inc. (DNR),DNR
                    NYSE Equity,Designer Brands Inc. (DBI),DBI
                    NYSE Equity,"Despegar.com, Corp. (DESP)",DESP
                    NYSE Equity,Deutsch Bk Contingent Cap Tr V (DKT),DKT
                    NYSE Equity,Deutsche Bank AG (DB),DB
                    NYSE Equity,Deutsche Bank AG (DXB),DXB
                    NYSE Equity,Devon Energy Corporation (DVN),DVN
                    NYSE Equity,"DHI Group, Inc. (DHX)",DHX
                    NYSE Equity,"DHT Holdings, Inc. (DHT)",DHT
                    NYSE Equity,Diageo plc (DEO),DEO
                    NYSE Equity,"Diamond Offshore Drilling, Inc. (DO)",DO
                    NYSE Equity,Diamond S Shipping Inc. (DSSI),DSSI
                    NYSE Equity,Diamondrock Hospitality Company (DRH),DRH
                    NYSE Equity,Diana Shipping inc. (DSX),DSX
                    NYSE Equity,Diana Shipping inc. (DSX^B),DSX^B
                    NYSE Equity,Dick&#39;s Sporting Goods Inc (DKS),DKS
                    NYSE Equity,Diebold Nixdorf Incorporated (DBD),DBD
                    NYSE Equity,"Digital Realty Trust, Inc. (DLR)",DLR
                    NYSE Equity,"Digital Realty Trust, Inc. (DLR^C)",DLR^C
                    NYSE Equity,"Digital Realty Trust, Inc. (DLR^G)",DLR^G
                    NYSE Equity,"Digital Realty Trust, Inc. (DLR^I)",DLR^I
                    NYSE Equity,"Digital Realty Trust, Inc. (DLR^J)",DLR^J
                    NYSE Equity,"Digital Realty Trust, Inc. (DLR^K)",DLR^K
                    NYSE Equity,"Dillard&#39;s, Inc. (DDS)",DDS
                    NYSE Equity,"Dillard&#39;s, Inc. (DDT)",DDT
                    NYSE Equity,"Dine Brands Global, Inc. (DIN)",DIN
                    NYSE Equity,"Diplomat Pharmacy, Inc. (DPLO)",DPLO
                    NYSE Equity,Discover Financial Services (DFS),DFS
                    NYSE Equity,Dividend and Income Fund (DNI),DNI
                    NYSE Equity,Dolby Laboratories (DLB),DLB
                    NYSE Equity,Dollar General Corporation (DG),DG
                    NYSE Equity,"Dominion Energy, Inc. (D)",D
                    NYSE Equity,"Dominion Energy, Inc. (DCUD)",DCUD
                    NYSE Equity,"Dominion Energy, Inc. (DCUE)",DCUE
                    NYSE Equity,"Dominion Energy, Inc. (DRUA)",DRUA
                    NYSE Equity,Domino&#39;s Pizza Inc (DPZ),DPZ
                    NYSE Equity,Domtar Corporation (UFS),UFS
                    NYSE Equity,"Donaldson Company, Inc. (DCI)",DCI
                    NYSE Equity,"Donnelley Financial Solutions, Inc. (DFIN)",DFIN
                    NYSE Equity,Dorian LPG Ltd. (LPG),LPG
                    NYSE Equity,DoubleLine Income Solutions Fund (DSL),DSL
                    NYSE Equity,DoubleLine Opportunistic Credit Fund (DBL),DBL
                    NYSE Equity,"Douglas Dynamics, Inc. (PLOW)",PLOW
                    NYSE Equity,"Douglas Emmett, Inc. (DEI)",DEI
                    NYSE Equity,Dover Corporation (DOV),DOV
                    NYSE Equity,"Dover Motorsports, Inc. (DVD)",DVD
                    NYSE Equity,Dow Inc. (DOW),DOW
                    NYSE Equity,Dr. Reddy&#39;s Laboratories Ltd (RDY),RDY
                    NYSE Equity,DRDGOLD Limited (DRD),DRD
                    NYSE Equity,"Dril-Quip, Inc. (DRQ)",DRQ
                    NYSE Equity,Drive Shack Inc. (DS),DS
                    NYSE Equity,Drive Shack Inc. (DS^B),DS^B
                    NYSE Equity,Drive Shack Inc. (DS^C),DS^C
                    NYSE Equity,Drive Shack Inc. (DS^D),DS^D
                    NYSE Equity,DTE Energy Company (DTE),DTE
                    NYSE Equity,DTE Energy Company (DTJ),DTJ
                    NYSE Equity,DTE Energy Company (DTQ),DTQ
                    NYSE Equity,DTE Energy Company (DTV),DTV
                    NYSE Equity,DTE Energy Company (DTW),DTW
                    NYSE Equity,DTE Energy Company (DTY),DTY
                    NYSE Equity,Ducommun Incorporated (DCO),DCO
                    NYSE Equity,Duff & Phelps Global Utility Income Fund Inc. (DPG),DPG
                    NYSE Equity,Duff & Phelps Select MLP and Midstream Energy Fund (DSE),DSE
                    NYSE Equity,"Duff & Phelps Utilities Income, Inc. (DNP)",DNP
                    NYSE Equity,"Duff & Phelps Utilities Tax-Free Income, Inc. (DTF)",DTF
                    NYSE Equity,"Duff & Phelps Utility & Corporate Bond Trust, Inc. (DUC)",DUC
                    NYSE Equity,Duke Energy Corporation (DUK),DUK
                    NYSE Equity,Duke Energy Corporation (DUK^A),DUK^A
                    NYSE Equity,Duke Energy Corporation (DUKB),DUKB
                    NYSE Equity,Duke Energy Corporation (DUKH),DUKH
                    NYSE Equity,Duke Realty Corporation (DRE),DRE
                    NYSE Equity,"DuPont de Nemours, Inc. (DD)",DD
                    NYSE Equity,DXC Technology Company (DXC),DXC
                    NYSE Equity,"Dycom Industries, Inc. (DY)",DY
                    NYSE Equity,Dynagas LNG Partners LP (DLNG),DLNG
                    NYSE Equity,Dynagas LNG Partners LP (DLNG^A),DLNG^A
                    NYSE Equity,Dynagas LNG Partners LP (DLNG^B),DLNG^B
                    NYSE Equity,"Dynex Capital, Inc. (DX)",DX
                    NYSE Equity,"Dynex Capital, Inc. (DX^A)",DX^A
                    NYSE Equity,"Dynex Capital, Inc. (DX^B)",DX^B
                    NYSE Equity,E.I. du Pont de Nemours and Company (CTA^A),CTA^A
                    NYSE Equity,E.I. du Pont de Nemours and Company (CTA^B),CTA^B
                    NYSE Equity,"e.l.f. Beauty, Inc. (ELF)",ELF
                    NYSE Equity,Eagle Growth and Income Opportunities Fund (EGIF),EGIF
                    NYSE Equity,Eagle Materials Inc (EXP),EXP
                    NYSE Equity,Eagle Point Credit Company Inc. (ECC           ),ECC           
                    NYSE Equity,Eagle Point Credit Company Inc. (ECCA),ECCA
                    NYSE Equity,Eagle Point Credit Company Inc. (ECCB),ECCB
                    NYSE Equity,Eagle Point Credit Company Inc. (ECCX),ECCX
                    NYSE Equity,Eagle Point Credit Company Inc. (ECCY),ECCY
                    NYSE Equity,"Earthstone Energy, Inc. (ESTE)",ESTE
                    NYSE Equity,"Easterly Government Properties, Inc. (DEA)",DEA
                    NYSE Equity,"EastGroup Properties, Inc. (EGP)",EGP
                    NYSE Equity,Eastman Chemical Company (EMN),EMN
                    NYSE Equity,Eastman Kodak Company (KODK),KODK
                    NYSE Equity,"Eaton Corporation, PLC (ETN)",ETN
                    NYSE Equity,Eaton Vance Corporation (ETV),ETV
                    NYSE Equity,Eaton Vance Corporation (ETW),ETW
                    NYSE Equity,Eaton Vance Corporation (EV),EV
                    NYSE Equity,Eaton Vance Enhance Equity Income Fund (EOI),EOI
                    NYSE Equity,Eaton Vance Enhanced Equity Income Fund II (EOS),EOS
                    NYSE Equity,Eaton Vance Floating Rate Income Trust (EFT),EFT
                    NYSE Equity,Eaton Vance Floating-Rate 2022 Target Term Trust (EFL),EFL
                    NYSE Equity,Eaton vance Floating-Rate Income Plus Fund (EFF),EFF
                    NYSE Equity,Eaton Vance High Income 2021 Target Term Trust (EHT),EHT
                    NYSE Equity,Eaton Vance Municipal Income 2028 Term Trust (ETX           ),ETX           
                    NYSE Equity,Eaton Vance Municipal Income Trust (EOT),EOT
                    NYSE Equity,Eaton Vance Municipal Income Trust (EVN),EVN
                    NYSE Equity,Eaton Vance Risk-Managed Diversified Equity Income Fund (ETJ),ETJ
                    NYSE Equity,Eaton Vance Senior Floating-Rate Fund (EFR),EFR
                    NYSE Equity,Eaton Vance Senior Income Trust (EVF),EVF
                    NYSE Equity,Eaton Vance Short Diversified Income Fund (EVG),EVG
                    NYSE Equity,Eaton Vance Tax Advantaged Dividend Income Fund (EVT),EVT
                    NYSE Equity,Eaton Vance Tax-Advantage Global Dividend Opp (ETO),ETO
                    NYSE Equity,Eaton Vance Tax-Advantaged Global Dividend Income Fund (ETG),ETG
                    NYSE Equity,Eaton Vance Tax-Managed Buy-Write Income Fund (ETB),ETB
                    NYSE Equity,Eaton Vance Tax-Managed Buy-Write Strategy Fund (EXD),EXD
                    NYSE Equity,Eaton Vance Tax-Managed Diversified Equity Income Fund (ETY),ETY
                    NYSE Equity,Eaton Vance Tax-Managed Global Diversified Equity Income Fund (EXG),EXG
                    NYSE Equity,ECA Marcellus Trust I (ECT),ECT
                    NYSE Equity,Ecolab Inc. (ECL),ECL
                    NYSE Equity,Ecopetrol S.A. (EC),EC
                    NYSE Equity,Edison International (EIX),EIX
                    NYSE Equity,Edwards Lifesciences Corporation (EW),EW
                    NYSE Equity,El Paso Corporation (EP^C),EP^C
                    NYSE Equity,El Paso Electric Company (EE),EE
                    NYSE Equity,Elanco Animal Health Incorporated (ELAN),ELAN
                    NYSE Equity,Elastic N.V. (ESTC),ESTC
                    NYSE Equity,Eldorado Gold Corporation (EGO),EGO
                    NYSE Equity,Element Solutions Inc. (ESI),ESI
                    NYSE Equity,"Elevate Credit, Inc. (ELVT)",ELVT
                    NYSE Equity,Eli Lilly and Company (LLY),LLY
                    NYSE Equity,Ellington Financial Inc. (EFC),EFC
                    NYSE Equity,Ellington Residential Mortgage REIT (EARN),EARN
                    NYSE Equity,Embotelladora Andina S.A. (AKO.A),AKO.A
                    NYSE Equity,Embotelladora Andina S.A. (AKO.B),AKO.B
                    NYSE Equity,Embraer S.A. (ERJ),ERJ
                    NYSE Equity,"EMCOR Group, Inc. (EME)",EME
                    NYSE Equity,"Emerald Expositions Events, Inc. (EEX)",EEX
                    NYSE Equity,"Emergent Biosolutions, Inc. (EBS)",EBS
                    NYSE Equity,Emerson Electric Company (EMR),EMR
                    NYSE Equity,"Empire State Realty Trust, Inc. (ESRT)",ESRT
                    NYSE Equity,Employers Holdings Inc (EIG),EIG
                    NYSE Equity,Empresa Distribuidora Y Comercializadora Norte S.A. (Edenor) (EDN),EDN
                    NYSE Equity,"Enable Midstream Partners, LP (ENBL)",ENBL
                    NYSE Equity,Enbridge Inc (ENB),ENB
                    NYSE Equity,Enbridge Inc (ENBA),ENBA
                    NYSE Equity,Encana Corporation (ECA),ECA
                    NYSE Equity,Encompass Health Corporation (EHC),EHC
                    NYSE Equity,Endava plc (DAVA),DAVA
                    NYSE Equity,Endeavour Silver Corporation (EXK),EXK
                    NYSE Equity,Enel Americas S.A. (ENIA),ENIA
                    NYSE Equity,Enel Chile S.A. (ENIC),ENIC
                    NYSE Equity,"Energizer Holdings, Inc. (ENR)",ENR
                    NYSE Equity,"Energizer Holdings, Inc. (ENR^A)",ENR^A
                    NYSE Equity,"Energizer Holdings, Inc. (EPC)",EPC
                    NYSE Equity,Energy Transfer L.P. (ET),ET
                    NYSE Equity,"Energy Transfer Operating, L.P. (ETP^C)",ETP^C
                    NYSE Equity,"Energy Transfer Operating, L.P. (ETP^D)",ETP^D
                    NYSE Equity,"Energy Transfer Operating, L.P. (ETP^E)",ETP^E
                    NYSE Equity,Enerplus Corporation (ERF),ERF
                    NYSE Equity,Enersys (ENS),ENS
                    NYSE Equity,ENI S.p.A. (E),E
                    NYSE Equity,"EnLink Midstream, LLC (ENLC)",ENLC
                    NYSE Equity,"Ennis, Inc. (EBF)",EBF
                    NYSE Equity,"Enova International, Inc. (ENVA)",ENVA
                    NYSE Equity,EnPro Industries (NPO),NPO
                    NYSE Equity,Ensco Rowan plc (ESV),ESV
                    NYSE Equity,Entercom Communications Corp. (ETM),ETM
                    NYSE Equity,"Entergy Arkansas, LLC (EAB)",EAB
                    NYSE Equity,"Entergy Arkansas, LLC (EAE)",EAE
                    NYSE Equity,"Entergy Arkansas, LLC (EAI)",EAI
                    NYSE Equity,Entergy Corporation (ETR),ETR
                    NYSE Equity,"Entergy Louisiana, Inc. (ELC)",ELC
                    NYSE Equity,"Entergy Louisiana, Inc. (ELJ)",ELJ
                    NYSE Equity,"Entergy Louisiana, Inc. (ELU)",ELU
                    NYSE Equity,"Entergy Mississippi, LLC (EMP)",EMP
                    NYSE Equity,"Entergy New Orleans, LLC (ENJ)",ENJ
                    NYSE Equity,"Entergy New Orleans, LLC (ENO)",ENO
                    NYSE Equity,Entergy Texas Inc (EZT),EZT
                    NYSE Equity,Enterprise Products Partners L.P. (EPD),EPD
                    NYSE Equity,Entravision Communications Corporation (EVC),EVC
                    NYSE Equity,"Envestnet, Inc (ENV)",ENV
                    NYSE Equity,"Enviva Partners, LP (EVA)",EVA
                    NYSE Equity,"Enzo Biochem, Inc. (ENZ)",ENZ
                    NYSE Equity,"EOG Resources, Inc. (EOG)",EOG
                    NYSE Equity,"EPAM Systems, Inc. (EPAM)",EPAM
                    NYSE Equity,EPR Properties (EPR),EPR
                    NYSE Equity,EPR Properties (EPR^C),EPR^C
                    NYSE Equity,EPR Properties (EPR^E),EPR^E
                    NYSE Equity,EPR Properties (EPR^G),EPR^G
                    NYSE Equity,"EQM Midstream Partners, LP (EQM)",EQM
                    NYSE Equity,EQT Corporation (EQT),EQT
                    NYSE Equity,"Equifax, Inc. (EFX)",EFX
                    NYSE Equity,Equinor ASA (EQNR),EQNR
                    NYSE Equity,Equitrans Midstream Corporation (ETRN),ETRN
                    NYSE Equity,Equity Commonwealth (EQC),EQC
                    NYSE Equity,Equity Commonwealth (EQC^D),EQC^D
                    NYSE Equity,"Equity Lifestyle Properties, Inc. (ELS)",ELS
                    NYSE Equity,Equity Residential (EQR),EQR
                    NYSE Equity,"Equus Total Return, Inc. (EQS)",EQS
                    NYSE Equity,"Era Group, Inc. (ERA)",ERA
                    NYSE Equity,Eros International PLC (EROS),EROS
                    NYSE Equity,ESCO Technologies Inc. (ESE),ESE
                    NYSE Equity,Essent Group Ltd. (ESNT),ESNT
                    NYSE Equity,"Essential Properties Realty Trust, Inc. (EPRT)",EPRT
                    NYSE Equity,"Essex Property Trust, Inc. (ESS)",ESS
                    NYSE Equity,"Estee Lauder Companies, Inc. (The) (EL)",EL
                    NYSE Equity,Ethan Allen Interiors Inc. (ETH),ETH
                    NYSE Equity,Euronav NV (EURN),EURN
                    NYSE Equity,"European Equity Fund, Inc. (The) (EEA)",EEA
                    NYSE Equity,"Eventbrite, Inc. (EB)",EB
                    NYSE Equity,Evercore Inc. (EVR),EVR
                    NYSE Equity,"Everest Re Group, Ltd. (RE)",RE
                    NYSE Equity,"Evergy, Inc. (EVRG)",EVRG
                    NYSE Equity,Everi Holdings Inc. (EVRI),EVRI
                    NYSE Equity,Eversource Energy (ES),ES
                    NYSE Equity,"Evertec, Inc. (EVTC)",EVTC
                    NYSE Equity,"Evolent Health, Inc (EVH)",EVH
                    NYSE Equity,Evoqua Water Technologies Corp. (AQUA),AQUA
                    NYSE Equity,Exantas Capital Corp. (XAN),XAN
                    NYSE Equity,Exantas Capital Corp. (XAN^C),XAN^C
                    NYSE Equity,Exelon Corporation (EXC),EXC
                    NYSE Equity,"Express, Inc. (EXPR)",EXPR
                    NYSE Equity,Exterran Corporation (EXTN),EXTN
                    NYSE Equity,Extra Space Storage Inc (EXR),EXR
                    NYSE Equity,Exxon Mobil Corporation (XOM),XOM
                    NYSE Equity,F.N.B. Corporation (FNB),FNB
                    NYSE Equity,F.N.B. Corporation (FNB^E),FNB^E
                    NYSE Equity,Fabrinet (FN),FN
                    NYSE Equity,FactSet Research Systems Inc. (FDS),FDS
                    NYSE Equity,Fair Isaac Corporation (FICO),FICO
                    NYSE Equity,Fang Holdings Limited (SFUN),SFUN
                    NYSE Equity,Far Point Acquisition Corporation (FPAC),FPAC
                    NYSE Equity,Far Point Acquisition Corporation (FPAC.U),FPAC.U
                    NYSE Equity,Far Point Acquisition Corporation (FPAC.WS),FPAC.WS
                    NYSE Equity,Farfetch Limited (FTCH),FTCH
                    NYSE Equity,Farmland Partners Inc. (FPI),FPI
                    NYSE Equity,Farmland Partners Inc. (FPI^B),FPI^B
                    NYSE Equity,"Fastly, Inc. (FSLY)",FSLY
                    NYSE Equity,FB Financial Corporation (FBK),FBK
                    NYSE Equity,"FBL Financial Group, Inc. (FFG)",FFG
                    NYSE Equity,Federal Agricultural Mortgage Corporation (AGM),AGM
                    NYSE Equity,Federal Agricultural Mortgage Corporation (AGM.A),AGM.A
                    NYSE Equity,Federal Agricultural Mortgage Corporation (AGM^A),AGM^A
                    NYSE Equity,Federal Agricultural Mortgage Corporation (AGM^C),AGM^C
                    NYSE Equity,Federal Agricultural Mortgage Corporation (AGM^D),AGM^D
                    NYSE Equity,Federal Realty Investment Trust (FRT),FRT
                    NYSE Equity,Federal Realty Investment Trust (FRT^C),FRT^C
                    NYSE Equity,Federal Signal Corporation (FSS),FSS
                    NYSE Equity,"Federated Investors, Inc. (FII)",FII
                    NYSE Equity,Federated Premier Municipal Income Fund (FMN),FMN
                    NYSE Equity,FedEx Corporation (FDX),FDX
                    NYSE Equity,Ferrari N.V. (RACE),RACE
                    NYSE Equity,"Ferrellgas Partners, L.P. (FGP)",FGP
                    NYSE Equity,Ferro Corporation (FOE),FOE
                    NYSE Equity,FGL Holdings (FG),FG
                    NYSE Equity,FGL Holdings (FG.WS),FG.WS
                    NYSE Equity,Fiat Chrysler Automobiles N.V. (FCAU),FCAU
                    NYSE Equity,"Fidelity National Financial, Inc. (FNF)",FNF
                    NYSE Equity,"Fidelity National Information Services, Inc. (FIS)",FIS
                    NYSE Equity,Fiduciary/Claymore Energy Infrastructure Fund (FMO),FMO
                    NYSE Equity,First American Corporation (The) (FAF),FAF
                    NYSE Equity,First BanCorp. (FBP),FBP
                    NYSE Equity,First Commonwealth Financial Corporation (FCF),FCF
                    NYSE Equity,First Data Corporation (FDC),FDC
                    NYSE Equity,First Horizon National Corporation (FHN),FHN
                    NYSE Equity,First Horizon National Corporation (FHN^A),FHN^A
                    NYSE Equity,"First Industrial Realty Trust, Inc. (FR)",FR
                    NYSE Equity,First Majestic Silver Corp. (AG),AG
                    NYSE Equity,FIRST REPUBLIC BANK (FRC),FRC
                    NYSE Equity,FIRST REPUBLIC BANK (FRC^D),FRC^D
                    NYSE Equity,FIRST REPUBLIC BANK (FRC^F),FRC^F
                    NYSE Equity,FIRST REPUBLIC BANK (FRC^G),FRC^G
                    NYSE Equity,FIRST REPUBLIC BANK (FRC^H),FRC^H
                    NYSE Equity,FIRST REPUBLIC BANK (FRC^I),FRC^I
                    NYSE Equity,First Trust (FFA),FFA
                    NYSE Equity,First Trust (FMY),FMY
                    NYSE Equity,First Trust Dynamic Europe Equity Income Fund (FDEU),FDEU
                    NYSE Equity,First Trust Energy Infrastructure Fund (FIF),FIF
                    NYSE Equity,First Trust High Income Long Short Fund (FSD),FSD
                    NYSE Equity,First Trust Intermediate Duration Preferred & Income Fund (FPF),FPF
                    NYSE Equity,First Trust MLP and Energy Income Fund (FEI           ),FEI           
                    NYSE Equity,First Trust New Opportunities MLP & Energy Fund (FPL),FPL
                    NYSE Equity,First Trust Senior Floating Rate 2022 Target Term Fund (FIV),FIV
                    NYSE Equity,First Trust Senior Floating Rate Income Fund II (FCT),FCT
                    NYSE Equity,First Trust Specialty Finance and Financial Opportunities Fund (FGB),FGB
                    NYSE Equity,First Trust/Aberdeen Emerging Opportunity Fund (FEO),FEO
                    NYSE Equity,First Trust/Aberdeen Global Opportunity Income Fund (FAM),FAM
                    NYSE Equity,FirstEnergy Corp. (FE),FE
                    NYSE Equity,"Fitbit, Inc. (FIT)",FIT
                    NYSE Equity,"Five Point Holdings, LLC (FPH)",FPH
                    NYSE Equity,Fiverr International Ltd. (FVRR),FVRR
                    NYSE Equity,"Flagstar Bancorp, Inc. (FBC)",FBC
                    NYSE Equity,Flaherty & Crumrine Dynamic Preferred and Income Fund Inc. (DFP),DFP
                    NYSE Equity,Flaherty & Crumrine Preferred Income Fund Incorporated (PFD),PFD
                    NYSE Equity,Flaherty & Crumrine Preferred Income Opportunity Fund Inc (PFO),PFO
                    NYSE Equity,Flaherty & Crumrine Preferred Securities Income Fund Inc (FFC),FFC
                    NYSE Equity,Flaherty & Crumrine Total Return Fund Inc (FLC),FLC
                    NYSE Equity,"FleetCor Technologies, Inc. (FLT)",FLT
                    NYSE Equity,FLEX LNG Ltd. (FLNG),FLNG
                    NYSE Equity,"Floor & Decor Holdings, Inc. (FND)",FND
                    NYSE Equity,"Flotek Industries, Inc. (FTK)",FTK
                    NYSE Equity,"Flowers Foods, Inc. (FLO)",FLO
                    NYSE Equity,Flowserve Corporation (FLS),FLS
                    NYSE Equity,Fluor Corporation (FLR),FLR
                    NYSE Equity,Fly Leasing Limited (FLY),FLY
                    NYSE Equity,FMC Corporation (FMC),FMC
                    NYSE Equity,Fomento Economico Mexicano S.A.B. de C.V. (FMX),FMX
                    NYSE Equity,"Foot Locker, Inc. (FL)",FL
                    NYSE Equity,Ford Motor Company (F),F
                    NYSE Equity,Ford Motor Company (F^B),F^B
                    NYSE Equity,Foresight Energy LP (FELP),FELP
                    NYSE Equity,Forestar Group Inc (FOR),FOR
                    NYSE Equity,Fortis Inc. (FTS),FTS
                    NYSE Equity,Fortive Corporation (FTV),FTV
                    NYSE Equity,Fortive Corporation (FTV^A),FTV^A
                    NYSE Equity,Fortress Transportation and Infrastructure Investors LLC (FTAI),FTAI
                    NYSE Equity,Fortuna Silver Mines Inc. (FSM),FSM
                    NYSE Equity,"Fortune Brands Home & Security, Inc. (FBHS)",FBHS
                    NYSE Equity,"Forum Energy Technologies, Inc. (FET)",FET
                    NYSE Equity,"Foundation Building Materials, Inc. (FBM)",FBM
                    NYSE Equity,"Four Corners Property Trust, Inc. (FCPT)",FCPT
                    NYSE Equity,Four Seasons Education (Cayman) Inc. (FEDU),FEDU
                    NYSE Equity,Franco-Nevada Corporation (FNV),FNV
                    NYSE Equity,Franklin Covey Company (FC),FC
                    NYSE Equity,"Franklin Financial Network, Inc. (FSB)",FSB
                    NYSE Equity,"Franklin Resources, Inc. (BEN)",BEN
                    NYSE Equity,Franklin Universal Trust (FT),FT
                    NYSE Equity,Frank&#39;s International N.V. (FI),FI
                    NYSE Equity,"Freeport-McMoran, Inc. (FCX)",FCX
                    NYSE Equity,Fresenius Medical Care Corporation (FMS),FMS
                    NYSE Equity,"Fresh Del Monte Produce, Inc. (FDP)",FDP
                    NYSE Equity,Front Yard Residential Corporation (RESI),RESI
                    NYSE Equity,Frontline Ltd. (FRO),FRO
                    NYSE Equity,FS KKR Capital Corp. (FSK),FSK
                    NYSE Equity,"FTI Consulting, Inc. (FCN)",FCN
                    NYSE Equity,"FTS International, Inc. (FTSI)",FTSI
                    NYSE Equity,FutureFuel Corp. (FF),FF
                    NYSE Equity,"Gabelli Convertible and Income Securities Fund, Inc. (The) (GCV)",GCV
                    NYSE Equity,"Gabelli Convertible and Income Securities Fund, Inc. (The) (GCV^B)",GCV^B
                    NYSE Equity,"Gabelli Equity Trust, Inc. (The) (GAB)",GAB
                    NYSE Equity,"Gabelli Equity Trust, Inc. (The) (GAB^D)",GAB^D
                    NYSE Equity,"Gabelli Equity Trust, Inc. (The) (GAB^G)",GAB^G
                    NYSE Equity,"Gabelli Equity Trust, Inc. (The) (GAB^H)",GAB^H
                    NYSE Equity,"Gabelli Equity Trust, Inc. (The) (GAB^J)",GAB^J
                    NYSE Equity,Gabelli Global Small and Mid Cap Value Trust (The) (GGZ),GGZ
                    NYSE Equity,Gabelli Global Small and Mid Cap Value Trust (The) (GGZ^A),GGZ^A
                    NYSE Equity,Gabelli Multi-Media Trust Inc. (The) (GGT),GGT
                    NYSE Equity,Gabelli Multi-Media Trust Inc. (The) (GGT^B),GGT^B
                    NYSE Equity,Gabelli Multi-Media Trust Inc. (The) (GGT^E),GGT^E
                    NYSE Equity,Gabelli Utility Trust (The) (GUT),GUT
                    NYSE Equity,Gabelli Utility Trust (The) (GUT^A),GUT^A
                    NYSE Equity,Gabelli Utility Trust (The) (GUT^C),GUT^C
                    NYSE Equity,"GAIN Capital Holdings, Inc. (GCAP)",GCAP
                    NYSE Equity,"Gamco Investors, Inc. (GBL)",GBL
                    NYSE Equity,"GAMCO Natural Resources, Gold & Income Tust  (GNT)",GNT
                    NYSE Equity,"GAMCO Natural Resources, Gold & Income Tust  (GNT^A)",GNT^A
                    NYSE Equity,Gamestop Corporation (GME),GME
                    NYSE Equity,"Gap, Inc. (The) (GPS)",GPS
                    NYSE Equity,"Gardner Denver Holdings, Inc. (GDI)",GDI
                    NYSE Equity,Garrett Motion Inc. (GTX),GTX
                    NYSE Equity,"Gartner, Inc. (IT)",IT
                    NYSE Equity,GasLog LP. (GLOG),GLOG
                    NYSE Equity,GasLog LP. (GLOG^A),GLOG^A
                    NYSE Equity,GasLog Partners LP (GLOP),GLOP
                    NYSE Equity,GasLog Partners LP (GLOP^A),GLOP^A
                    NYSE Equity,GasLog Partners LP (GLOP^B),GLOP^B
                    NYSE Equity,GasLog Partners LP (GLOP^C),GLOP^C
                    NYSE Equity,Gates Industrial Corporation plc (GTES),GTES
                    NYSE Equity,GATX Corporation (GATX),GATX
                    NYSE Equity,GATX Corporation (GMTA),GMTA
                    NYSE Equity,GCP Applied Technologies Inc. (GCP),GCP
                    NYSE Equity,Genco Shipping & Trading Limited  (GNK),GNK
                    NYSE Equity,Generac Holdlings Inc. (GNRC),GNRC
                    NYSE Equity,"General American Investors, Inc. (GAM)",GAM
                    NYSE Equity,"General American Investors, Inc. (GAM^B)",GAM^B
                    NYSE Equity,General Dynamics Corporation (GD),GD
                    NYSE Equity,General Electric Company (GE),GE
                    NYSE Equity,"General Mills, Inc. (GIS)",GIS
                    NYSE Equity,General Motors Company (GM),GM
                    NYSE Equity,General Motors Company (GM.WS.B),GM.WS.B
                    NYSE Equity,Genesco Inc. (GCO),GCO
                    NYSE Equity,"Genesee & Wyoming, Inc. (GWR)",GWR
                    NYSE Equity,"Genesis Energy, L.P. (GEL)",GEL
                    NYSE Equity,"Genesis Healthcare, Inc. (GEN           )",GEN           
                    NYSE Equity,Genie Energy Ltd. (GNE),GNE
                    NYSE Equity,Genie Energy Ltd. (GNE^A),GNE^A
                    NYSE Equity,Genpact Limited (G),G
                    NYSE Equity,Genuine Parts Company (GPC),GPC
                    NYSE Equity,Genworth Financial Inc (GNW),GNW
                    NYSE Equity,Geo Group Inc (The) (GEO),GEO
                    NYSE Equity,Geopark Ltd (GPRK),GPRK
                    NYSE Equity,Georgia Power Company (GPJA),GPJA
                    NYSE Equity,Gerdau S.A. (GGB),GGB
                    NYSE Equity,Getty Realty Corporation (GTY),GTY
                    NYSE Equity,"GigCapital, Inc. (GIG)",GIG
                    NYSE Equity,"GigCapital, Inc. (GIG.U)",GIG.U
                    NYSE Equity,"GigCapital, Inc. (GIG.WS)",GIG.WS
                    NYSE Equity,"GigCapital, Inc. (GIG~)",GIG~
                    NYSE Equity,"GigCapital2, Inc. (GIX.U)",GIX.U
                    NYSE Equity,"Gildan Activewear, Inc. (GIL)",GIL
                    NYSE Equity,Glatfelter (GLT),GLT
                    NYSE Equity,Glaukos Corporation (GKOS),GKOS
                    NYSE Equity,GlaxoSmithKline PLC (GSK),GSK
                    NYSE Equity,"Global Brass and Copper Holdings, Inc. (BRSS)",BRSS
                    NYSE Equity,Global Cord Blood Corporation (CO),CO
                    NYSE Equity,Global Medical REIT Inc. (GMRE),GMRE
                    NYSE Equity,Global Medical REIT Inc. (GMRE^A),GMRE^A
                    NYSE Equity,"Global Net Lease, Inc. (GNL)",GNL
                    NYSE Equity,"Global Net Lease, Inc. (GNL^A)",GNL^A
                    NYSE Equity,Global Partners LP (GLP),GLP
                    NYSE Equity,Global Partners LP (GLP^A),GLP^A
                    NYSE Equity,Global Payments Inc. (GPN),GPN
                    NYSE Equity,"Global Ship Lease, Inc. (GSL)",GSL
                    NYSE Equity,"Global Ship Lease, Inc. (GSL^B)",GSL^B
                    NYSE Equity,Globant S.A. (GLOB),GLOB
                    NYSE Equity,"Globus Medical, Inc. (GMED)",GMED
                    NYSE Equity,GMS Inc. (GMS),GMS
                    NYSE Equity,"GNC Holdings, Inc. (GNC)",GNC
                    NYSE Equity,GoDaddy Inc. (GDDY),GDDY
                    NYSE Equity,Gol Linhas Aereas Inteligentes S.A. (GOL),GOL
                    NYSE Equity,Gold Fields Limited (GFI),GFI
                    NYSE Equity,"Goldman Sachs BDC, Inc. (GSBD)",GSBD
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS)",GS
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS^A)",GS^A
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS^B.CL)",GS^B.CL
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS^C)",GS^C
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS^D)",GS^D
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS^J)",GS^J
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS^K)",GS^K
                    NYSE Equity,"Goldman Sachs Group, Inc. (The) (GS^N)",GS^N
                    NYSE Equity,Goldman Sachs MLP Energy Renaissance Fund (GER),GER
                    NYSE Equity,Goldman Sachs MLP Income Opportunities Fund (GMZ),GMZ
                    NYSE Equity,Gorman-Rupp Company (The) (GRC),GRC
                    NYSE Equity,GP Strategies Corporation (GPX),GPX
                    NYSE Equity,Graco Inc. (GGG),GGG
                    NYSE Equity,Graf Industrial Corp. (GRAF),GRAF
                    NYSE Equity,Graf Industrial Corp. (GRAF.U),GRAF.U
                    NYSE Equity,Graf Industrial Corp. (GRAF.WS),GRAF.WS
                    NYSE Equity,GrafTech International Ltd. (EAF),EAF
                    NYSE Equity,Graham Corporation (GHM),GHM
                    NYSE Equity,Graham Holdings Company (GHC),GHC
                    NYSE Equity,Grana y Montero S.A.A. (GRAM),GRAM
                    NYSE Equity,Granite Construction Incorporated (GVA),GVA
                    NYSE Equity,Granite Point Mortgage Trust Inc. (GPMT),GPMT
                    NYSE Equity,Granite Real Estate Inc. (GRP.U),GRP.U
                    NYSE Equity,Graphic Packaging Holding Company (GPK),GPK
                    NYSE Equity,"Gray Television, Inc. (GTN)",GTN
                    NYSE Equity,"Gray Television, Inc. (GTN.A)",GTN.A
                    NYSE Equity,Great Ajax Corp. (AJX),AJX
                    NYSE Equity,Great Ajax Corp. (AJXA),AJXA
                    NYSE Equity,"Great Western Bancorp, Inc. (GWB)",GWB
                    NYSE Equity,Green Dot Corporation (GDOT),GDOT
                    NYSE Equity,"Greenbrier Companies, Inc. (The) (GBX)",GBX
                    NYSE Equity,"Greenhill & Co., Inc. (GHL)",GHL
                    NYSE Equity,GreenTree Hospitality Group Ltd. (GHG),GHG
                    NYSE Equity,Greif Bros. Corporation (GEF),GEF
                    NYSE Equity,Greif Bros. Corporation (GEF.B),GEF.B
                    NYSE Equity,Griffon Corporation (GFF),GFF
                    NYSE Equity,"Group 1 Automotive, Inc. (GPI)",GPI
                    NYSE Equity,GrubHub Inc. (GRUB),GRUB
                    NYSE Equity,"Grupo Aeroportuario Del Pacifico, S.A. de C.V. (PAC)",PAC
                    NYSE Equity,"Grupo Aeroportuario del Sureste, S.A. de C.V. (ASR)",ASR
                    NYSE Equity,Grupo Aval Acciones y Valores S.A. (AVAL),AVAL
                    NYSE Equity,Grupo Supervielle S.A. (SUPV),SUPV
                    NYSE Equity,Grupo Televisa S.A. (TV),TV
                    NYSE Equity,GS Acquisition Holdings Corp. (GSAH),GSAH
                    NYSE Equity,GS Acquisition Holdings Corp. (GSAH.U),GSAH.U
                    NYSE Equity,GS Acquisition Holdings Corp. (GSAH.WS),GSAH.WS
                    NYSE Equity,GSX Techedu Inc. (GSX),GSX
                    NYSE Equity,"GTT Communications, Inc. (GTT)",GTT
                    NYSE Equity,Guangshen Railway Company Limited (GSH),GSH
                    NYSE Equity,"Guess?, Inc. (GES)",GES
                    NYSE Equity,Guggenheim Credit Allocation Fund (GGM),GGM
                    NYSE Equity,Guggenheim Enhanced Equity Income Fund (GPM),GPM
                    NYSE Equity,Guggenheim Strategic Opportunities Fund (GOF),GOF
                    NYSE Equity,Guggenheim Taxable Municipal Managed Duration Trst (GBAB),GBAB
                    NYSE Equity,"Guidewire Software, Inc. (GWRE)",GWRE
                    NYSE Equity,"H&R Block, Inc. (HRB)",HRB
                    NYSE Equity,H. B. Fuller Company (FUL),FUL
                    NYSE Equity,Haemonetics Corporation (HAE),HAE
                    NYSE Equity,Halcon Resources Corporation (HK),HK
                    NYSE Equity,Halcon Resources Corporation (HK.WS),HK.WS
                    NYSE Equity,Halliburton Company (HAL),HAL
                    NYSE Equity,Hamilton Beach Brands Holding Company (HBB),HBB
                    NYSE Equity,Hanesbrands Inc. (HBI),HBI
                    NYSE Equity,"Hanger, Inc. (HNGR)",HNGR
                    NYSE Equity,"Hannon Armstrong Sustainable Infrastructure Capital, Inc. (HASI)",HASI
                    NYSE Equity,"Harley-Davidson, Inc. (HOG)",HOG
                    NYSE Equity,Harmony Gold Mining Company Limited (HMY),HMY
                    NYSE Equity,Harris Corporation (HRS),HRS
                    NYSE Equity,Harsco Corporation (HSC),HSC
                    NYSE Equity,"Harte-Hanks, Inc. (HHS)",HHS
                    NYSE Equity,"Hartford Financial Services Group, Inc. (The) (HGH)",HGH
                    NYSE Equity,"Hartford Financial Services Group, Inc. (The) (HIG)",HIG
                    NYSE Equity,"Hartford Financial Services Group, Inc. (The) (HIG^G)",HIG^G
                    NYSE Equity,"Haverty Furniture Companies, Inc. (HVT)",HVT
                    NYSE Equity,"Haverty Furniture Companies, Inc. (HVT.A)",HVT.A
                    NYSE Equity,"Hawaiian Electric Industries, Inc. (HE)",HE
                    NYSE Equity,"HC2 Holdings, Inc. (HCHC)",HCHC
                    NYSE Equity,"HCA Healthcare, Inc. (HCA)",HCA
                    NYSE Equity,"HCI Group, Inc. (HCI)",HCI
                    NYSE Equity,"HCP, Inc. (HCP)",HCP
                    NYSE Equity,HDFC Bank Limited (HDB),HDB
                    NYSE Equity,Healthcare Realty Trust Incorporated (HR),HR
                    NYSE Equity,"Healthcare Trust of America, Inc. (HTA)",HTA
                    NYSE Equity,Hecla Mining Company (HL),HL
                    NYSE Equity,Hecla Mining Company (HL^B),HL^B
                    NYSE Equity,Heico Corporation (HEI),HEI
                    NYSE Equity,Heico Corporation (HEI.A),HEI.A
                    NYSE Equity,"Helix Energy Solutions Group, Inc. (HLX)",HLX
                    NYSE Equity,"Helmerich & Payne, Inc. (HP)",HP
                    NYSE Equity,Herbalife Nutrition Ltd. (HLF),HLF
                    NYSE Equity,Herc Holdings Inc. (HRI),HRI
                    NYSE Equity,"Hercules Capital, Inc. (HCXY)",HCXY
                    NYSE Equity,"Hercules Capital, Inc. (HCXZ)",HCXZ
                    NYSE Equity,"Hercules Capital, Inc. (HTGC)",HTGC
                    NYSE Equity,"Heritage Insurance Holdings, Inc. (HRTG)",HRTG
                    NYSE Equity,Hermitage Offshore Services Ltd. (PSV),PSV
                    NYSE Equity,Hersha Hospitality Trust (HT),HT
                    NYSE Equity,Hersha Hospitality Trust (HT^C),HT^C
                    NYSE Equity,Hersha Hospitality Trust (HT^D),HT^D
                    NYSE Equity,Hersha Hospitality Trust (HT^E),HT^E
                    NYSE Equity,Hershey Company (The) (HSY),HSY
                    NYSE Equity,"Hertz Global Holdings, Inc (HTZ)",HTZ
                    NYSE Equity,"Hertz Global Holdings, Inc (HTZ~$)",HTZ~$
                    NYSE Equity,Hess Corporation (HES),HES
                    NYSE Equity,Hess Midstream Partners LP (HESM),HESM
                    NYSE Equity,Hewlett Packard Enterprise Company (HPE),HPE
                    NYSE Equity,Hexcel Corporation (HXL),HXL
                    NYSE Equity,"HFF, Inc. (HF)",HF
                    NYSE Equity,Hi-Crush Inc. (HCR),HCR
                    NYSE Equity,High Income Securities Fund (PCF),PCF
                    NYSE Equity,Highland Global Allocation Fund (HGLB),HGLB
                    NYSE Equity,Highland Income Fund (HFRO),HFRO
                    NYSE Equity,HighPoint Resources Corporation (HPR),HPR
                    NYSE Equity,"Highwoods Properties, Inc. (HIW)",HIW
                    NYSE Equity,"Hill International, Inc. (HIL)",HIL
                    NYSE Equity,Hillenbrand Inc (HI),HI
                    NYSE Equity,Hill-Rom Holdings Inc (HRC),HRC
                    NYSE Equity,Hilltop Holdings Inc. (HTH),HTH
                    NYSE Equity,Hilton Grand Vacations Inc. (HGV),HGV
                    NYSE Equity,Hilton Worldwide Holdings Inc. (HLT),HLT
                    NYSE Equity,HNI Corporation (HNI),HNI
                    NYSE Equity,Hoegh LNG Partners LP (HMLP),HMLP
                    NYSE Equity,Hoegh LNG Partners LP (HMLP^A),HMLP^A
                    NYSE Equity,"Holly Energy Partners, L.P. (HEP)",HEP
                    NYSE Equity,HollyFrontier Corporation (HFC),HFC
                    NYSE Equity,"Home Depot, Inc. (The) (HD)",HD
                    NYSE Equity,"Honda Motor Company, Ltd. (HMC)",HMC
                    NYSE Equity,Honeywell International Inc. (HON),HON
                    NYSE Equity,Horace Mann Educators Corporation (HMN),HMN
                    NYSE Equity,Horizon Global Corporation (HZN),HZN
                    NYSE Equity,Horizon Technology Finance Corporation (HTFA),HTFA
                    NYSE Equity,Hormel Foods Corporation (HRL),HRL
                    NYSE Equity,Hornbeck Offshore Services (HOS),HOS
                    NYSE Equity,"Host Hotels & Resorts, Inc. (HST)",HST
                    NYSE Equity,"Houlihan Lokey, Inc. (HLI)",HLI
                    NYSE Equity,Hovnanian Enterprises Inc (HOV),HOV
                    NYSE Equity,Howard Hughes Corporation (The) (HHC),HHC
                    NYSE Equity,HP Inc. (HPQ),HPQ
                    NYSE Equity,HSBC Holdings plc (HSBC),HSBC
                    NYSE Equity,HSBC Holdings plc (HSBC^A),HSBC^A
                    NYSE Equity,Huami Corporation (HMI),HMI
                    NYSE Equity,"Huaneng Power International, Inc. (HNP)",HNP
                    NYSE Equity,Hubbell Inc (HUBB),HUBB
                    NYSE Equity,"HubSpot, Inc. (HUBS)",HUBS
                    NYSE Equity,Hudbay Minerals Inc. (HBM),HBM
                    NYSE Equity,Hudson Ltd. (HUD),HUD
                    NYSE Equity,"Hudson Pacific Properties, Inc. (HPP)",HPP
                    NYSE Equity,Humana Inc. (HUM),HUM
                    NYSE Equity,"Hunt Companies Finance Trust, Inc. (HCFT)",HCFT
                    NYSE Equity,"Huntington Ingalls Industries, Inc. (HII)",HII
                    NYSE Equity,Huntsman Corporation (HUN),HUN
                    NYSE Equity,HUYA Inc. (HUYA),HUYA
                    NYSE Equity,Hyatt Hotels Corporation (H),H
                    NYSE Equity,"Hyster-Yale Materials Handling, Inc. (HY)",HY
                    NYSE Equity,"IAA, Inc. (IAA$)",IAA$
                    NYSE Equity,Iamgold Corporation (IAG),IAG
                    NYSE Equity,ICICI Bank Limited (IBN),IBN
                    NYSE Equity,"IDACORP, Inc. (IDA)",IDA
                    NYSE Equity,IDEX Corporation (IEX),IEX
                    NYSE Equity,IDT Corporation (IDT),IDT
                    NYSE Equity,Illinois Tool Works Inc. (ITW),ITW
                    NYSE Equity,Imax Corporation (IMAX),IMAX
                    NYSE Equity,"Independence Contract Drilling, Inc. (ICD)",ICD
                    NYSE Equity,Independence Holding Company (IHC),IHC
                    NYSE Equity,"Independence Realty Trust, Inc. (IRT)",IRT
                    NYSE Equity,"India Fund, Inc. (The) (IFN)",IFN
                    NYSE Equity,"Industrias Bachoco, S.A. de C.V. (IBA)",IBA
                    NYSE Equity,Infosys Limited (INFY),INFY
                    NYSE Equity,"ING Group, N.V. (ING)",ING
                    NYSE Equity,"ING Group, N.V. (ISG)",ISG
                    NYSE Equity,Ingersoll-Rand plc (Ireland) (IR),IR
                    NYSE Equity,Ingevity Corporation (NGVT),NGVT
                    NYSE Equity,Ingredion Incorporated (INGR),INGR
                    NYSE Equity,"Innovative Industrial Properties, Inc. (IIPR)",IIPR
                    NYSE Equity,"Innovative Industrial Properties, Inc. (IIPR^A)",IIPR^A
                    NYSE Equity,Inphi Corporation (IPHI),IPHI
                    NYSE Equity,Insight Select Income Fund (INSI),INSI
                    NYSE Equity,"Insperity, Inc. (NSP)",NSP
                    NYSE Equity,"Inspire Medical Systems, Inc. (INSP)",INSP
                    NYSE Equity,"Installed Building Products, Inc. (IBP)",IBP
                    NYSE Equity,"Instructure, Inc. (INST)",INST
                    NYSE Equity,Integer Holdings Corporation (ITGR),ITGR
                    NYSE Equity,Intelsat S.A. (I),I
                    NYSE Equity,Intercontinental Exchange Inc. (ICE),ICE
                    NYSE Equity,Intercontinental Hotels Group (IHG),IHG
                    NYSE Equity,International Business Machines Corporation (IBM),IBM
                    NYSE Equity,"International Flavors & Fragrances, Inc. (IFF)",IFF
                    NYSE Equity,"International Flavors & Fragrances, Inc. (IFFT)",IFFT
                    NYSE Equity,International Game Technology (IGT),IGT
                    NYSE Equity,International Paper Company (IP),IP
                    NYSE Equity,"International Seaways, Inc. (INSW)",INSW
                    NYSE Equity,"International Seaways, Inc. (INSW^A)",INSW^A
                    NYSE Equity,"Interpublic Group of Companies, Inc. (The) (IPG)",IPG
                    NYSE Equity,InterXion Holding N.V. (INXN),INXN
                    NYSE Equity,"Intrepid Potash, Inc (IPI)",IPI
                    NYSE Equity,Invacare Corporation (IVC),IVC
                    NYSE Equity,Invesco Bond Fund (VBF),VBF
                    NYSE Equity,Invesco California Value Municipal Income Trust (VCV),VCV
                    NYSE Equity,Invesco Credit Opportunities Fund (VTA),VTA
                    NYSE Equity,Invesco High Income 2023 Target Term Fund (IHIT),IHIT
                    NYSE Equity,Invesco High Income 2024 Target Term Fund (IHTA),IHTA
                    NYSE Equity,Invesco High Income Trust II (VLT),VLT
                    NYSE Equity,INVESCO MORTGAGE CAPITAL INC (IVR),IVR
                    NYSE Equity,INVESCO MORTGAGE CAPITAL INC (IVR^B),IVR^B
                    NYSE Equity,INVESCO MORTGAGE CAPITAL INC (IVR^C),IVR^C
                    NYSE Equity,Invesco Mortgage Capital Inc. (IVR^A),IVR^A
                    NYSE Equity,Invesco Municipal Income Opportunities Trust (OIA),OIA
                    NYSE Equity,Invesco Municipal Opportunity Trust (VMO),VMO
                    NYSE Equity,Invesco Municipal Trust (VKQ),VKQ
                    NYSE Equity,Invesco Pennsylvania Value Municipal Income Trust (VPV),VPV
                    NYSE Equity,Invesco Plc (IVZ),IVZ
                    NYSE Equity,Invesco Quality Municipal Income Trust (IQI),IQI
                    NYSE Equity,Invesco Senior Income Trust (VVR),VVR
                    NYSE Equity,Invesco Trust  for Investment Grade New York Municipal (VTN),VTN
                    NYSE Equity,Invesco Trust for Investment Grade Municipals (VGM),VGM
                    NYSE Equity,Invesco Value Municipal Income Trust (IIM),IIM
                    NYSE Equity,Investors Real Estate Trust (IRET),IRET
                    NYSE Equity,Investors Real Estate Trust (IRET^C),IRET^C
                    NYSE Equity,Invitae Corporation (NVTA),NVTA
                    NYSE Equity,Invitation Homes Inc. (INVH),INVH
                    NYSE Equity,Ion Geophysical Corporation (IO),IO
                    NYSE Equity,"IQVIA Holdings, Inc. (IQV)",IQV
                    NYSE Equity,Iron Mountain Incorporated (IRM),IRM
                    NYSE Equity,IRSA Inversiones Y Representaciones S.A. (IRS),IRS
                    NYSE Equity,Israel Chemicals Shs (ICL),ICL
                    NYSE Equity,iStar Inc. (STAR          ),STAR          
                    NYSE Equity,iStar Inc. (STAR^D),STAR^D
                    NYSE Equity,iStar Inc. (STAR^G),STAR^G
                    NYSE Equity,iStar Inc. (STAR^I),STAR^I
                    NYSE Equity,Ita? CorpBanca (ITCB),ITCB
                    NYSE Equity,Itau Unibanco Banco Holding SA (ITUB),ITUB
                    NYSE Equity,ITT Inc. (ITT),ITT
                    NYSE Equity,Ivy High Income Opportunities Fund (IVH),IVH
                    NYSE Equity,J P Morgan Chase & Co (JPM),JPM
                    NYSE Equity,J P Morgan Chase & Co (JPM^A),JPM^A
                    NYSE Equity,J P Morgan Chase & Co (JPM^C),JPM^C
                    NYSE Equity,J P Morgan Chase & Co (JPM^D),JPM^D
                    NYSE Equity,J P Morgan Chase & Co (JPM^E),JPM^E
                    NYSE Equity,J P Morgan Chase & Co (JPM^F),JPM^F
                    NYSE Equity,J P Morgan Chase & Co (JPM^G),JPM^G
                    NYSE Equity,J P Morgan Chase & Co (JPM^H),JPM^H
                    NYSE Equity,"J. Alexander&#39;s Holdings, Inc. (JAX)",JAX
                    NYSE Equity,"J. Jill, Inc. (JILL)",JILL
                    NYSE Equity,"J.C. Penney Company, Inc. Holding Company (JCP)",JCP
                    NYSE Equity,J.M. Smucker Company (The) (SJM),SJM
                    NYSE Equity,Jabil Inc. (JBL),JBL
                    NYSE Equity,Jacobs Engineering Group Inc. (JEC),JEC
                    NYSE Equity,Jagged Peak Energy Inc. (JAG),JAG
                    NYSE Equity,James Hardie Industries plc. (JHX),JHX
                    NYSE Equity,Janus Henderson Group plc (JHG),JHG
                    NYSE Equity,Japan Smaller Capitalization Fund Inc (JOF),JOF
                    NYSE Equity,JBG SMITH Properties (JBGS),JBGS
                    NYSE Equity,Jefferies Financial Group Inc. (JEF),JEF
                    NYSE Equity,"JELD-WEN Holding, Inc. (JELD)",JELD
                    NYSE Equity,"Jernigan Capital, Inc. (JCAP)",JCAP
                    NYSE Equity,"Jernigan Capital, Inc. (JCAP^B)",JCAP^B
                    NYSE Equity,Jianpu Technology Inc. (JT),JT
                    NYSE Equity,JinkoSolar Holding Company Limited (JKS),JKS
                    NYSE Equity,JMP Group LLC (JMP),JMP
                    NYSE Equity,JMP Group LLC (JMPB),JMPB
                    NYSE Equity,JMP Group LLC (JMPD),JMPD
                    NYSE Equity,John Bean Technologies Corporation (JBT),JBT
                    NYSE Equity,John Hancock Financial Opportunities Fund (BTO),BTO
                    NYSE Equity,John Hancock Hedged Equity & Income Fund (HEQ),HEQ
                    NYSE Equity,John Hancock Income Securities Trust (JHS),JHS
                    NYSE Equity,John Hancock Investors Trust (JHI),JHI
                    NYSE Equity,John Hancock Pfd Income Fund II (HPF),HPF
                    NYSE Equity,John Hancock Preferred Income Fund (HPI),HPI
                    NYSE Equity,John Hancock Preferred Income Fund III (HPS),HPS
                    NYSE Equity,John Hancock Premium Dividend Fund (PDT),PDT
                    NYSE Equity,John Hancock Tax Advantaged Dividend Income Fund (HTD),HTD
                    NYSE Equity,John Hancock Tax-Advantaged Global Shareholder Yield Fund (HTY),HTY
                    NYSE Equity,"John Wiley & Sons, Inc. (JW.A)",JW.A
                    NYSE Equity,"John Wiley & Sons, Inc. (JW.B)",JW.B
                    NYSE Equity,Johnson & Johnson (JNJ),JNJ
                    NYSE Equity,Johnson Controls International plc (JCI),JCI
                    NYSE Equity,Jones Lang LaSalle Incorporated (JLL),JLL
                    NYSE Equity,Jumei International Holding Limited (JMEI),JMEI
                    NYSE Equity,Jumia Technologies AG (JMIA),JMIA
                    NYSE Equity,"Juniper Networks, Inc. (JNPR)",JNPR
                    NYSE Equity,Jupai Holdings Limited (JP),JP
                    NYSE Equity,"Just Energy Group, Inc. (JE)",JE
                    NYSE Equity,"Just Energy Group, Inc. (JE^A)",JE^A
                    NYSE Equity,K12 Inc (LRN),LRN
                    NYSE Equity,Kadant Inc (KAI),KAI
                    NYSE Equity,"Kadmon Holdings, Inc. (KDMN)",KDMN
                    NYSE Equity,Kaman Corporation (KAMN),KAMN
                    NYSE Equity,Kansas City Southern (KSU),KSU
                    NYSE Equity,Kansas City Southern (KSU^),KSU^
                    NYSE Equity,"KAR Auction Services, Inc (KAR)",KAR
                    NYSE Equity,"KAR Auction Services, Inc (KAR$)",KAR$
                    NYSE Equity,"Kayne Anderson Midstream Energy Fund, Inc (KMF)",KMF
                    NYSE Equity,Kayne Anderson MLP/Midstream Investment Company (KYN),KYN
                    NYSE Equity,Kayne Anderson MLP/Midstream Investment Company (KYN^F),KYN^F
                    NYSE Equity,KB Financial Group Inc (KB),KB
                    NYSE Equity,KB Home (KBH),KBH
                    NYSE Equity,"KBR, Inc. (KBR)",KBR
                    NYSE Equity,"Keane Group, Inc. (FRAC)",FRAC
                    NYSE Equity,Kellogg Company (K),K
                    NYSE Equity,Kemet Corporation (KEM),KEM
                    NYSE Equity,Kemper Corporation (KMPA),KMPA
                    NYSE Equity,Kemper Corporation (KMPR),KMPR
                    NYSE Equity,Kennametal Inc. (KMT),KMT
                    NYSE Equity,Kennedy-Wilson Holdings Inc. (KW),KW
                    NYSE Equity,Kenon Holdings Ltd. (KEN),KEN
                    NYSE Equity,Keurig Dr Pepper Inc. (KDP),KDP
                    NYSE Equity,"Key Energy Services, Inc. (KEG)",KEG
                    NYSE Equity,KeyCorp (KEY),KEY
                    NYSE Equity,KeyCorp (KEY^I),KEY^I
                    NYSE Equity,KeyCorp (KEY^J),KEY^J
                    NYSE Equity,KeyCorp (KEY^K),KEY^K
                    NYSE Equity,Keysight Technologies Inc. (KEYS),KEYS
                    NYSE Equity,Kilroy Realty Corporation (KRC),KRC
                    NYSE Equity,Kimbell Royalty Partners (KRP),KRP
                    NYSE Equity,Kimberly-Clark Corporation (KMB),KMB
                    NYSE Equity,Kimco Realty Corporation (KIM),KIM
                    NYSE Equity,Kimco Realty Corporation (KIM^I),KIM^I
                    NYSE Equity,Kimco Realty Corporation (KIM^J),KIM^J
                    NYSE Equity,Kimco Realty Corporation (KIM^K),KIM^K
                    NYSE Equity,Kimco Realty Corporation (KIM^L),KIM^L
                    NYSE Equity,Kimco Realty Corporation (KIM^M),KIM^M
                    NYSE Equity,"Kinder Morgan, Inc. (KMI)",KMI
                    NYSE Equity,"Kingsway Financial Services, Inc. (KFS)",KFS
                    NYSE Equity,Kinross Gold Corporation (KGC),KGC
                    NYSE Equity,Kirby Corporation (KEX),KEX
                    NYSE Equity,Kirkland Lake Gold Ltd. (KL),KL
                    NYSE Equity,Kite Realty Group Trust (KRG),KRG
                    NYSE Equity,KKR & Co. Inc. (KKR),KKR
                    NYSE Equity,KKR & Co. Inc. (KKR^A),KKR^A
                    NYSE Equity,KKR & Co. Inc. (KKR^B),KKR^B
                    NYSE Equity,KKR Income Opportunities Fund (KIO),KIO
                    NYSE Equity,KKR Real Estate Finance Trust Inc. (KREF),KREF
                    NYSE Equity,"Knight Transportation, Inc. (KNX)",KNX
                    NYSE Equity,"Knoll, Inc. (KNL)",KNL
                    NYSE Equity,KNOT Offshore Partners LP (KNOP),KNOP
                    NYSE Equity,Knowles Corporation (KN),KN
                    NYSE Equity,Kohl&#39;s Corporation (KSS),KSS
                    NYSE Equity,Koninklijke Philips N.V. (PHG),PHG
                    NYSE Equity,"Kontoor Brands, Inc. (KTB)",KTB
                    NYSE Equity,Koppers Holdings Inc. (KOP),KOP
                    NYSE Equity,Korea Electric Power Corporation (KEP),KEP
                    NYSE Equity,"Korea Fund, Inc. (The) (KF)",KF
                    NYSE Equity,Korn Ferry  (KFY),KFY
                    NYSE Equity,Kosmos Energy Ltd. (KOS),KOS
                    NYSE Equity,Kraton Corporation (KRA),KRA
                    NYSE Equity,Kroger Company (The) (KR),KR
                    NYSE Equity,Kronos Worldwide Inc (KRO),KRO
                    NYSE Equity,KT Corporation (KT),KT
                    NYSE Equity,"L Brands, Inc. (LB)",LB
                    NYSE Equity,L.S. Starrett Company (The) (SCX),SCX
                    NYSE Equity,"L3 Technologies, Inc. (LLL)",LLL
                    NYSE Equity,Laboratory Corporation of America Holdings (LH),LH
                    NYSE Equity,Ladder Capital Corp (LADR),LADR
                    NYSE Equity,LAIX Inc. (LAIX),LAIX
                    NYSE Equity,"Lamb Weston Holdings, Inc. (LW)",LW
                    NYSE Equity,Lannett Co Inc (LCI),LCI
                    NYSE Equity,"Laredo Petroleum, Inc. (LPI)",LPI
                    NYSE Equity,Las Vegas Sands Corp. (LVS),LVS
                    NYSE Equity,LATAM Airlines Group S.A. (LTM),LTM
                    NYSE Equity,Lazard Global Total Return and Income Fund (LGI),LGI
                    NYSE Equity,Lazard Ltd. (LAZ),LAZ
                    NYSE Equity,"Lazard World Dividend & Income Fund, Inc. (LOR)",LOR
                    NYSE Equity,La-Z-Boy Incorporated (LZB),LZB
                    NYSE Equity,LCI Industries  (LCII),LCII
                    NYSE Equity,Leaf Group Ltd. (LEAF),LEAF
                    NYSE Equity,Lear Corporation (LEA),LEA
                    NYSE Equity,"Lee Enterprises, Incorporated (LEE)",LEE
                    NYSE Equity,Legacy Acquisition Corp. (LGC),LGC
                    NYSE Equity,Legacy Acquisition Corp. (LGC.U),LGC.U
                    NYSE Equity,Legacy Acquisition Corp. (LGC.WS),LGC.WS
                    NYSE Equity,"Legg Mason, Inc. (LM)",LM
                    NYSE Equity,"Legg Mason, Inc. (LMHA)",LMHA
                    NYSE Equity,"Legg Mason, Inc. (LMHB)",LMHB
                    NYSE Equity,"Leggett & Platt, Incorporated (LEG)",LEG
                    NYSE Equity,Lehman ABS Corporation (JBK),JBK
                    NYSE Equity,Lehman ABS Corporation (KTH),KTH
                    NYSE Equity,Lehman ABS Corporation (KTN),KTN
                    NYSE Equity,Lehman ABS Corporation (KTP),KTP
                    NYSE Equity,"Leidos Holdings, Inc. (LDOS)",LDOS
                    NYSE Equity,Leju Holdings Limited (LEJU),LEJU
                    NYSE Equity,LendingClub Corporation (LC),LC
                    NYSE Equity,Lennar Corporation (LEN),LEN
                    NYSE Equity,Lennar Corporation (LEN.B),LEN.B
                    NYSE Equity,"Lennox International, Inc. (LII)",LII
                    NYSE Equity,Leo Holdings Corp. (LHC),LHC
                    NYSE Equity,Leo Holdings Corp. (LHC.U),LHC.U
                    NYSE Equity,Leo Holdings Corp. (LHC.WS),LHC.WS
                    NYSE Equity,Levi Strauss & Co (LEVI),LEVI
                    NYSE Equity,Lexington Realty Trust (LXP),LXP
                    NYSE Equity,Lexington Realty Trust (LXP^C),LXP^C
                    NYSE Equity,"LG Display Co., Ltd. (LPL)",LPL
                    NYSE Equity,Liberty All-Star Equity Fund (USA),USA
                    NYSE Equity,"Liberty All-Star Growth Fund, Inc. (ASG)",ASG
                    NYSE Equity,Liberty Oilfield Services Inc. (LBRT),LBRT
                    NYSE Equity,Liberty Property Trust (LPT),LPT
                    NYSE Equity,"Life Storage, Inc. (LSI)",LSI
                    NYSE Equity,"LightInTheBox Holding Co., Ltd. (LITB)",LITB
                    NYSE Equity,Lincoln National Corporation (LNC),LNC
                    NYSE Equity,Lincoln National Corporation (LNC.WS),LNC.WS
                    NYSE Equity,Linde plc (LIN),LIN
                    NYSE Equity,Lindsay Corporation (LNN),LNN
                    NYSE Equity,LINE Corporation (LN),LN
                    NYSE Equity,Lions Gate Entertainment Corporation (LGF.A),LGF.A
                    NYSE Equity,Lions Gate Entertainment Corporation (LGF.B),LGF.B
                    NYSE Equity,"Lithia Motors, Inc. (LAD)",LAD
                    NYSE Equity,Lithium Americas Corp. (LAC),LAC
                    NYSE Equity,"Live Nation Entertainment, Inc. (LYV)",LYV
                    NYSE Equity,Livent Corporation (LTHM),LTHM
                    NYSE Equity,"LiveRamp Holdings, Inc. (RAMP)",RAMP
                    NYSE Equity,Lloyds Banking Group Plc (LYG),LYG
                    NYSE Equity,LMP Capital and Income Fund Inc. (SCD),SCD
                    NYSE Equity,Lockheed Martin Corporation (LMT),LMT
                    NYSE Equity,Loews Corporation (L),L
                    NYSE Equity,Loma Negra Compania Industrial Argentina Sociedad Anonima (LOMA),LOMA
                    NYSE Equity,Louisiana-Pacific Corporation (LPX),LPX
                    NYSE Equity,"Lowe&#39;s Companies, Inc. (LOW)",LOW
                    NYSE Equity,Lsb Industries Inc. (LXU),LXU
                    NYSE Equity,"LSC Communications, Inc. (LKSD)",LKSD
                    NYSE Equity,"LTC Properties, Inc. (LTC)",LTC
                    NYSE Equity,"Luby&#39;s, Inc. (LUB)",LUB
                    NYSE Equity,"Lumber Liquidators Holdings, Inc (LL)",LL
                    NYSE Equity,Luxfer Holdings PLC (LXFR),LXFR
                    NYSE Equity,"Lydall, Inc. (LDL)",LDL
                    NYSE Equity,Lyon William Homes (WLH),WLH
                    NYSE Equity,LyondellBasell Industries NV (LYB),LYB
                    NYSE Equity,M&T Bank Corporation (MTB),MTB
                    NYSE Equity,M&T Bank Corporation (MTB^),MTB^
                    NYSE Equity,M&T Bank Corporation (MTB^C),MTB^C
                    NYSE Equity,"M.D.C. Holdings, Inc. (MDC)",MDC
                    NYSE Equity,"M/I Homes, Inc. (MHO)",MHO
                    NYSE Equity,Macerich Company (The) (MAC),MAC
                    NYSE Equity,Mack-Cali Realty Corporation (CLI),CLI
                    NYSE Equity,Macquarie First Trust Global (MFD),MFD
                    NYSE Equity,Macquarie Global Infrastructure Total Return Fund Inc. (MGU),MGU
                    NYSE Equity,Macquarie Infrastructure Corporation  (MIC),MIC
                    NYSE Equity,Macro Bank Inc. (BMA),BMA
                    NYSE Equity,Macy&#39;s Inc (M),M
                    NYSE Equity,Madison Covered Call & Equity Strategy Fund (MCN),MCN
                    NYSE Equity,Magellan Midstream Partners L.P. (MMP),MMP
                    NYSE Equity,"Magna International, Inc. (MGA)",MGA
                    NYSE Equity,MagnaChip Semiconductor Corporation (MX),MX
                    NYSE Equity,Magnolia Oil & Gas Corporation (MGY),MGY
                    NYSE Equity,Magnolia Oil & Gas Corporation (MGY.WS),MGY.WS
                    NYSE Equity,"Maiden Holdings, Ltd. (MH^A)",MH^A
                    NYSE Equity,"Maiden Holdings, Ltd. (MH^C)",MH^C
                    NYSE Equity,"Maiden Holdings, Ltd. (MH^D)",MH^D
                    NYSE Equity,"Maiden Holdings, Ltd. (MHLA)",MHLA
                    NYSE Equity,"Maiden Holdings, Ltd. (MHNC)",MHNC
                    NYSE Equity,Main Street Capital Corporation (MAIN),MAIN
                    NYSE Equity,MainStay MacKay DefinedTerm Municipal Opportunitie (MMD),MMD
                    NYSE Equity,Mallinckrodt plc (MNK),MNK
                    NYSE Equity,Manchester United Ltd. (MANU),MANU
                    NYSE Equity,"Manitowoc Company, Inc. (The) (MTW)",MTW
                    NYSE Equity,"Manning & Napier, Inc. (MN)",MN
                    NYSE Equity,ManpowerGroup (MAN),MAN
                    NYSE Equity,Manulife Financial Corp (MFC),MFC
                    NYSE Equity,Marathon Oil Corporation (MRO),MRO
                    NYSE Equity,Marathon Petroleum Corporation (MPC),MPC
                    NYSE Equity,"Marcus & Millichap, Inc. (MMI)",MMI
                    NYSE Equity,Marcus Corporation (The) (MCS),MCS
                    NYSE Equity,Marine Products Corporation (MPX),MPX
                    NYSE Equity,"MarineMax, Inc. (HZO)",HZO
                    NYSE Equity,Markel Corporation (MKL),MKL
                    NYSE Equity,Marriott Vacations Worldwide Corporation (VAC),VAC
                    NYSE Equity,"Marsh & McLennan Companies, Inc. (MMC)",MMC
                    NYSE Equity,"Martin Marietta Materials, Inc. (MLM)",MLM
                    NYSE Equity,Masco Corporation (MAS),MAS
                    NYSE Equity,Masonite International Corporation (DOOR),DOOR
                    NYSE Equity,"MasTec, Inc. (MTZ)",MTZ
                    NYSE Equity,Mastercard Incorporated (MA),MA
                    NYSE Equity,Matador Resources Company (MTDR),MTDR
                    NYSE Equity,Materion Corporation (MTRN),MTRN
                    NYSE Equity,"Matson, Inc. (MATX)",MATX
                    NYSE Equity,"Maui Land & Pineapple Company, Inc. (MLP)",MLP
                    NYSE Equity,Maxar Technologies Inc. (MAXR),MAXR
                    NYSE Equity,"Maximus, Inc. (MMS)",MMS
                    NYSE Equity,"MaxLinear, Inc (MXL)",MXL
                    NYSE Equity,"Mayville Engineering Company, Inc. (MEC)",MEC
                    NYSE Equity,"MBIA, Inc. (MBI)",MBI
                    NYSE Equity,"McCormick & Company, Incorporated (MKC)",MKC
                    NYSE Equity,"McCormick & Company, Incorporated (MKC.V)",MKC.V
                    NYSE Equity,"McDermott International, Inc. (MDR)",MDR
                    NYSE Equity,McDonald&#39;s Corporation (MCD),MCD
                    NYSE Equity,McEwen Mining Inc. (MUX),MUX
                    NYSE Equity,McKesson Corporation (MCK),MCK
                    NYSE Equity,"MDU Resources Group, Inc. (MDU)",MDU
                    NYSE Equity,Mechel PAO (MTL),MTL
                    NYSE Equity,Mechel PAO (MTL^),MTL^
                    NYSE Equity,"Medical Properties Trust, Inc. (MPW)",MPW
                    NYSE Equity,MEDIFAST INC (MED),MED
                    NYSE Equity,Medley Capital Corporation (MCC),MCC
                    NYSE Equity,Medley Capital Corporation (MCV),MCV
                    NYSE Equity,Medley Capital Corporation (MCX),MCX
                    NYSE Equity,Medley LLC (MDLQ),MDLQ
                    NYSE Equity,Medley LLC (MDLX),MDLX
                    NYSE Equity,Medley Management Inc. (MDLY),MDLY
                    NYSE Equity,"Mednax, Inc (MD)",MD
                    NYSE Equity,Medtronic plc (MDT),MDT
                    NYSE Equity,Megalith Financial Acquisition Corp. (MFAC),MFAC
                    NYSE Equity,Megalith Financial Acquisition Corp. (MFAC.U),MFAC.U
                    NYSE Equity,Megalith Financial Acquisition Corp. (MFAC.WS),MFAC.WS
                    NYSE Equity,"Merck & Company, Inc. (MRK)",MRK
                    NYSE Equity,Mercury General Corporation (MCY),MCY
                    NYSE Equity,Meredith Corporation (MDP),MDP
                    NYSE Equity,Meritage Corporation (MTH),MTH
                    NYSE Equity,"Meritor, Inc. (MTOR)",MTOR
                    NYSE Equity,"Merrill Lynch & Co., Inc. (MER^K)",MER^K
                    NYSE Equity,"Merrill Lynch Depositor, Inc. (PIY)",PIY
                    NYSE Equity,Mesa Royalty Trust (MTR),MTR
                    NYSE Equity,Mesabi Trust (MSB),MSB
                    NYSE Equity,"Methode Electronics, Inc. (MEI)",MEI
                    NYSE Equity,"MetLife, Inc. (MET)",MET
                    NYSE Equity,"MetLife, Inc. (MET^A)",MET^A
                    NYSE Equity,"MetLife, Inc. (MET^E)",MET^E
                    NYSE Equity,Metropolitan Bank Holding Corp. (MCB),MCB
                    NYSE Equity,"Mettler-Toledo International, Inc. (MTD)",MTD
                    NYSE Equity,"Mexico Equity and Income Fund, Inc. (The) (MXE)",MXE
                    NYSE Equity,"Mexico Fund, Inc. (The) (MXF)",MXF
                    NYSE Equity,"MFA Financial, Inc. (MFA)",MFA
                    NYSE Equity,"MFA Financial, Inc. (MFA^B)",MFA^B
                    NYSE Equity,"MFA Financial, Inc. (MFO)",MFO
                    NYSE Equity,MFS Charter Income Trust (MCR),MCR
                    NYSE Equity,MFS Government Markets Income Trust (MGF),MGF
                    NYSE Equity,MFS Intermediate Income Trust (MIN),MIN
                    NYSE Equity,MFS Multimarket Income Trust (MMT),MMT
                    NYSE Equity,MFS Municipal Income Trust (MFM),MFM
                    NYSE Equity,MFS Special Value Trust (MFV),MFV
                    NYSE Equity,MGIC Investment Corporation (MTG),MTG
                    NYSE Equity,MGM Growth Properties LLC (MGP),MGP
                    NYSE Equity,MGM Resorts International (MGM),MGM
                    NYSE Equity,Micro Focus Intl PLC (MFGP),MFGP
                    NYSE Equity,"Mid-America Apartment Communities, Inc. (MAA)",MAA
                    NYSE Equity,"Mid-America Apartment Communities, Inc. (MAA^I)",MAA^I
                    NYSE Equity,MidSouth Bancorp (MSL),MSL
                    NYSE Equity,"MIDSTATES PETROLEUM COMPANY, INC. (MPO)",MPO
                    NYSE Equity,Milacron Holdings Corp. (MCRN),MCRN
                    NYSE Equity,"Miller Industries, Inc. (MLR)",MLR
                    NYSE Equity,Miller/Howard High Income Equity Fund (HIE),HIE
                    NYSE Equity,Minerals Technologies Inc. (MTX),MTX
                    NYSE Equity,Mistras Group Inc (MG),MG
                    NYSE Equity,Mitsubishi UFJ Financial Group Inc (MUFG),MUFG
                    NYSE Equity,MiX Telematics Limited (MIXT),MIXT
                    NYSE Equity,"Mizuho Financial Group, Inc. (MFG)",MFG
                    NYSE Equity,Mobile TeleSystems OJSC (MBT),MBT
                    NYSE Equity,"Model N, Inc. (MODN)",MODN
                    NYSE Equity,Modine Manufacturing Company (MOD),MOD
                    NYSE Equity,Moelis & Company (MC),MC
                    NYSE Equity,MOGU Inc. (MOGU),MOGU
                    NYSE Equity,"Mohawk Industries, Inc. (MHK)",MHK
                    NYSE Equity,Molina Healthcare Inc (MOH),MOH
                    NYSE Equity,Molson Coors Brewing  Company (TAP),TAP
                    NYSE Equity,Molson Coors Brewing  Company (TAP.A),TAP.A
                    NYSE Equity,Monmouth Real Estate Investment Corporation (MNR),MNR
                    NYSE Equity,Monmouth Real Estate Investment Corporation (MNR^C),MNR^C
                    NYSE Equity,Montage Resources Corporation (MR),MR
                    NYSE Equity,Moody&#39;s Corporation (MCO),MCO
                    NYSE Equity,Moog Inc. (MOG.A),MOG.A
                    NYSE Equity,Moog Inc. (MOG.B),MOG.B
                    NYSE Equity,Morgan Stanley (MS),MS
                    NYSE Equity,Morgan Stanley (MS^A),MS^A
                    NYSE Equity,Morgan Stanley (MS^E),MS^E
                    NYSE Equity,Morgan Stanley (MS^F),MS^F
                    NYSE Equity,Morgan Stanley (MS^G),MS^G
                    NYSE Equity,Morgan Stanley (MS^I),MS^I
                    NYSE Equity,Morgan Stanley (MS^K),MS^K
                    NYSE Equity,Morgan Stanley China A Share Fund Inc. (CAF),CAF
                    NYSE Equity,"Morgan Stanley Emerging Markets Debt Fund, Inc. (MSD)",MSD
                    NYSE Equity,"Morgan Stanley Emerging Markets Domestic Debt Fund, Inc. (EDD)",EDD
                    NYSE Equity,"Morgan Stanley India Investment Fund, Inc. (IIF)",IIF
                    NYSE Equity,Mosaic Acquisition Corp. (MOSC),MOSC
                    NYSE Equity,Mosaic Acquisition Corp. (MOSC.U),MOSC.U
                    NYSE Equity,Mosaic Acquisition Corp. (MOSC.WS),MOSC.WS
                    NYSE Equity,Mosaic Company (The) (MOS),MOS
                    NYSE Equity,"Motorola Solutions, Inc. (MSI)",MSI
                    NYSE Equity,Movado Group Inc. (MOV),MOV
                    NYSE Equity,MPLX LP (MPLX),MPLX
                    NYSE Equity,MRC Global Inc. (MRC),MRC
                    NYSE Equity,MS Structured Asset Corp Saturns GE Cap Corp Series 2002-14 (HJV),HJV
                    NYSE Equity,MSA Safety Incorporporated (MSA),MSA
                    NYSE Equity,"MSC Industrial Direct Company, Inc. (MSM)",MSM
                    NYSE Equity,MSCI Inc (MSCI),MSCI
                    NYSE Equity,MSG Networks Inc. (MSGN),MSGN
                    NYSE Equity,"Mueller Industries, Inc. (MLI)",MLI
                    NYSE Equity,Mueller Water Products Inc (MWA),MWA
                    NYSE Equity,"MuniVest Fund, Inc. (MVF)",MVF
                    NYSE Equity,"MuniYield Arizona Fund, Inc. (MZA)",MZA
                    NYSE Equity,Murphy Oil Corporation (MUR),MUR
                    NYSE Equity,Murphy USA Inc. (MUSA),MUSA
                    NYSE Equity,MV Oil Trust (MVO),MVO
                    NYSE Equity,"MVC Capital, Inc. (MVC)",MVC
                    NYSE Equity,"MVC Capital, Inc. (MVCD)",MVCD
                    NYSE Equity,"Myers Industries, Inc. (MYE)",MYE
                    NYSE Equity,Myovant Sciences Ltd. (MYOV),MYOV
                    NYSE Equity,Nabors Industries Ltd. (NBR),NBR
                    NYSE Equity,Nabors Industries Ltd. (NBR^A),NBR^A
                    NYSE Equity,"NACCO Industries, Inc. (NC)",NC
                    NYSE Equity,Nam Tai Property Inc. (NTP),NTP
                    NYSE Equity,NASDAQ TEST STOCK (NTEST),NTEST
                    NYSE Equity,NASDAQ TEST STOCK (NTEST.A),NTEST.A
                    NYSE Equity,NASDAQ TEST STOCK (NTEST.B),NTEST.B
                    NYSE Equity,NASDAQ TEST STOCK (NTEST.C),NTEST.C
                    NYSE Equity,National Bank Holdings Corporation (NBHC),NBHC
                    NYSE Equity,National Fuel Gas Company (NFG),NFG
                    NYSE Equity,"National Grid Transco, PLC (NGG)",NGG
                    NYSE Equity,"National Health Investors, Inc. (NHI)",NHI
                    NYSE Equity,"National Oilwell Varco, Inc. (NOV)",NOV
                    NYSE Equity,"National Presto Industries, Inc. (NPK)",NPK
                    NYSE Equity,National Retail Properties (NNN),NNN
                    NYSE Equity,National Retail Properties (NNN^E),NNN^E
                    NYSE Equity,National Retail Properties (NNN^F),NNN^F
                    NYSE Equity,National Rural Utilities Cooperative Finance Corporation (NRUC),NRUC
                    NYSE Equity,National Steel Company (SID),SID
                    NYSE Equity,National Storage Affiliates Trust (NSA),NSA
                    NYSE Equity,National Storage Affiliates Trust (NSA^A),NSA^A
                    NYSE Equity,"Natural Gas Services Group, Inc. (NGS)",NGS
                    NYSE Equity,"Natural Grocers by Vitamin Cottage, Inc. (NGVC)",NGVC
                    NYSE Equity,Natural Resource Partners LP (NRP),NRP
                    NYSE Equity,"Natuzzi, S.p.A. (NTZ)",NTZ
                    NYSE Equity,"Nautilus Group, Inc. (The) (NLS)",NLS
                    NYSE Equity,"Navigant Consulting, Inc. (NCI)",NCI
                    NYSE Equity,Navigator Holdings Ltd. (NVGS),NVGS
                    NYSE Equity,Navios Maritime Acquisition Corporation (NNA),NNA
                    NYSE Equity,Navios Maritime Holdings Inc. (NM),NM
                    NYSE Equity,Navios Maritime Holdings Inc. (NM^G),NM^G
                    NYSE Equity,Navios Maritime Holdings Inc. (NM^H),NM^H
                    NYSE Equity,Navios Maritime Partners LP (NMM),NMM
                    NYSE Equity,Navistar International Corporation (NAV),NAV
                    NYSE Equity,Navistar International Corporation (NAV^D),NAV^D
                    NYSE Equity,NCR Corporation (NCR),NCR
                    NYSE Equity,"Neenah, Inc. (NP)",NP
                    NYSE Equity,"Nelnet, Inc. (NNI)",NNI
                    NYSE Equity,NeoPhotonics Corporation (NPTN),NPTN
                    NYSE Equity,Nevro Corp. (NVRO),NVRO
                    NYSE Equity,"New America High Income Fund, Inc. (The) (HYB)",HYB
                    NYSE Equity,New Frontier Corporation (NFC),NFC
                    NYSE Equity,New Frontier Corporation (NFC.U),NFC.U
                    NYSE Equity,New Frontier Corporation (NFC.WS),NFC.WS
                    NYSE Equity,"New Germany Fund, Inc. (The) (GF)",GF
                    NYSE Equity,New Home Company Inc. (The) (NWHM),NWHM
                    NYSE Equity,"New Ireland Fund, Inc. (The) (IRL)",IRL
                    NYSE Equity,New Media Investment Group Inc. (NEWM),NEWM
                    NYSE Equity,New Mountain Finance Corporation (NMFC),NMFC
                    NYSE Equity,New Mountain Finance Corporation (NMFX),NMFX
                    NYSE Equity,"New Oriental Education & Technology Group, Inc. (EDU)",EDU
                    NYSE Equity,"New Relic, Inc. (NEWR)",NEWR
                    NYSE Equity,New Residential Investment Corp. (NRZ),NRZ
                    NYSE Equity,New Senior Investment Group Inc. (SNR),SNR
                    NYSE Equity,"New York Community Bancorp, Inc. (NYCB)",NYCB
                    NYSE Equity,"New York Community Bancorp, Inc. (NYCB^A)",NYCB^A
                    NYSE Equity,"New York Community Bancorp, Inc. (NYCB^U)",NYCB^U
                    NYSE Equity,New York Times Company (The) (NYT),NYT
                    NYSE Equity,NewJersey Resources Corporation (NJR),NJR
                    NYSE Equity,NewMarket Corporation (NEU),NEU
                    NYSE Equity,Newmont Goldcorp Corporation (NEM),NEM
                    NYSE Equity,"Newpark Resources, Inc. (NR)",NR
                    NYSE Equity,Nexa Resources S.A. (NEXA),NEXA
                    NYSE Equity,"NexPoint Residential Trust, Inc. (NXRT)",NXRT
                    NYSE Equity,NexPoint Strategic Opportunities Fund (NHF),NHF
                    NYSE Equity,"NextEra Energy Partners, LP (NEP)",NEP
                    NYSE Equity,"NextEra Energy, Inc. (NEE)",NEE
                    NYSE Equity,"NextEra Energy, Inc. (NEE^I)",NEE^I
                    NYSE Equity,"NextEra Energy, Inc. (NEE^J)",NEE^J
                    NYSE Equity,"NextEra Energy, Inc. (NEE^K)",NEE^K
                    NYSE Equity,"NextEra Energy, Inc. (NEE^N)",NEE^N
                    NYSE Equity,"NextEra Energy, Inc. (NEE^R)",NEE^R
                    NYSE Equity,NGL ENERGY PARTNERS LP (NGL),NGL
                    NYSE Equity,NGL ENERGY PARTNERS LP (NGL^B),NGL^B
                    NYSE Equity,NGL ENERGY PARTNERS LP (NGL^C),NGL^C
                    NYSE Equity,"Niagara Mohawk Holdings, Inc. (NMK^B)",NMK^B
                    NYSE Equity,"Niagara Mohawk Holdings, Inc. (NMK^C)",NMK^C
                    NYSE Equity,Nielsen N.V. (NLSN),NLSN
                    NYSE Equity,"Nike, Inc. (NKE)",NKE
                    NYSE Equity,"Nine Energy Service, Inc. (NINE)",NINE
                    NYSE Equity,NIO Inc. (NIO),NIO
                    NYSE Equity,"NiSource, Inc (NI)",NI
                    NYSE Equity,"NiSource, Inc (NI^B)",NI^B
                    NYSE Equity,"NL Industries, Inc. (NL)",NL
                    NYSE Equity,Noah Holdings Ltd. (NOAH),NOAH
                    NYSE Equity,Noble Corporation (NE),NE
                    NYSE Equity,Noble Energy Inc. (NBL),NBL
                    NYSE Equity,Noble Midstream Partners LP (NBLX),NBLX
                    NYSE Equity,Nokia Corporation (NOK),NOK
                    NYSE Equity,Nomad Foods Limited (NOMD),NOMD
                    NYSE Equity,Nomura Holdings Inc ADR (NMR),NMR
                    NYSE Equity,Norbord Inc. (OSB),OSB
                    NYSE Equity,Nordic American Tankers Limited (NAT),NAT
                    NYSE Equity,"Nordstrom, Inc. (JWN)",JWN
                    NYSE Equity,Norfolk Souther Corporation (NSC),NSC
                    NYSE Equity,North American Construction Group Ltd. (NOA),NOA
                    NYSE Equity,North European Oil Royality Trust (NRT),NRT
                    NYSE Equity,Northrop Grumman Corporation (NOC),NOC
                    NYSE Equity,NorthStar Realty Europe Corp. (NRE),NRE
                    NYSE Equity,Northwest Natural Holding Company (NWN),NWN
                    NYSE Equity,NorthWestern Corporation (NWE),NWE
                    NYSE Equity,Norwegian Cruise Line Holdings Ltd. (NCLH),NCLH
                    NYSE Equity,Novartis AG (NVS),NVS
                    NYSE Equity,Novo Nordisk A/S (NVO),NVO
                    NYSE Equity,NOW Inc. (DNOW),DNOW
                    NYSE Equity,"NRG Energy, Inc. (NRG)",NRG
                    NYSE Equity,"Nu Skin Enterprises, Inc. (NUS)",NUS
                    NYSE Equity,Nucor Corporation (NUE),NUE
                    NYSE Equity,Nustar Energy L.P. (NS),NS
                    NYSE Equity,Nustar Energy L.P. (NS^A),NS^A
                    NYSE Equity,Nustar Energy L.P. (NS^B),NS^B
                    NYSE Equity,Nustar Energy L.P. (NS^C),NS^C
                    NYSE Equity,"NuStar Logistics, L.P. (NSS)",NSS
                    NYSE Equity,Nutrien Ltd. (NTR),NTR
                    NYSE Equity,Nuveen All Cap Energy MLP Opportunities Fund (JMLP),JMLP
                    NYSE Equity,Nuveen AMT-Free Municipal Credit Income Fund (NVG),NVG
                    NYSE Equity,Nuveen AMT-Free Municipal Value Fund (NUV),NUV
                    NYSE Equity,Nuveen AMT-Free Municipal Value Fund (NUW),NUW
                    NYSE Equity,Nuveen AMT-Free Quality Municipal Income Fund (NEA),NEA
                    NYSE Equity,Nuveen Arizona Quality Municipal Income Fund (NAZ),NAZ
                    NYSE Equity,Nuveen California AMT-Free Quality Municipal Income Fund (NKX),NKX
                    NYSE Equity,Nuveen California Municipal Value Fund 2 (NCB),NCB
                    NYSE Equity,"Nuveen California Municipal Value Fund, Inc. (NCA)",NCA
                    NYSE Equity,Nuveen California Quality Municipal Income Fund (NAC),NAC
                    NYSE Equity,Nuveen Connecticut Quality Municipal Income Fund (NTC),NTC
                    NYSE Equity,Nuveen Core Equity Alpha Fund (JCE),JCE
                    NYSE Equity,Nuveen Credit Opportunities 2022 Target Term Fund (JCO),JCO
                    NYSE Equity,Nuveen Credit Strategies Income Fund (JQC),JQC
                    NYSE Equity,Nuveen Diversified Dividend and Income Fund (JDD),JDD
                    NYSE Equity,Nuveen Dow 30SM Dynamic Overwrite Fund (DIAX),DIAX
                    NYSE Equity,Nuveen Emerging Markets Debt 2022 Target Term Fund (JEMD),JEMD
                    NYSE Equity,Nuveen Energy MLP Total Return Fund (JMF),JMF
                    NYSE Equity,Nuveen Enhanced Municipal Value Fund (NEV),NEV
                    NYSE Equity,Nuveen Floating Rate Income Fund (JFR),JFR
                    NYSE Equity,Nuveen Floating Rate Income Opportuntiy Fund (JRO),JRO
                    NYSE Equity,Nuveen Georgia Quality Municipal Income Fund  (NKG),NKG
                    NYSE Equity,Nuveen Global High Income Fund (JGH),JGH
                    NYSE Equity,Nuveen High Income 2020 Target Term Fund (JHY),JHY
                    NYSE Equity,Nuveen High Income 2023 Target Term Fund (JHAA),JHAA
                    NYSE Equity,Nuveen High Income December 2019 Target Term Fund (JHD),JHD
                    NYSE Equity,Nuveen High Income November 2021 Target Term Fund (JHB),JHB
                    NYSE Equity,Nuveen Insured California Select Tax-Free Income Portfolio (NXC),NXC
                    NYSE Equity,Nuveen Insured New York Select Tax-Free Income Portfolio (NXN),NXN
                    NYSE Equity,Nuveen Intermediate Duration Municipal Term Fund (NID),NID
                    NYSE Equity,Nuveen Maryland Quality Municipal Income Fund (NMY),NMY
                    NYSE Equity,Nuveen Massachusetts Municipal Income Fund (NMT),NMT
                    NYSE Equity,Nuveen Michigan Quality Municipal Income Fund (NUM),NUM
                    NYSE Equity,Nuveen Minnesota Quality Municipal Income Fund (NMS),NMS
                    NYSE Equity,Nuveen Missouri Quality Municipal Income Fund (NOM),NOM
                    NYSE Equity,Nuveen Mortgage Opportunity Term Fund (JLS),JLS
                    NYSE Equity,Nuveen Multi-Market Income Fund (JMM),JMM
                    NYSE Equity,Nuveen Municipal 2021 Target Term Fund (NHA),NHA
                    NYSE Equity,Nuveen Municipal Credit Income Fund (NZF),NZF
                    NYSE Equity,Nuveen Municipal High Income Opportunity Fund (NMZ),NMZ
                    NYSE Equity,"Nuveen Municipal Income Fund, Inc. (NMI)",NMI
                    NYSE Equity,Nuveen New Jersey Municipal Value Fund (NJV),NJV
                    NYSE Equity,Nuveen New Jersey Quality Municipal Income Fund (NXJ),NXJ
                    NYSE Equity,Nuveen New York AMT-Free Quality Municipal (NRK),NRK
                    NYSE Equity,Nuveen New York Municipal Value Fund 2 (NYV),NYV
                    NYSE Equity,"Nuveen New York Municipal Value Fund, Inc. (NNY)",NNY
                    NYSE Equity,Nuveen New York Quality Municipal Income Fund (NAN),NAN
                    NYSE Equity,Nuveen North Carolina Quality Municipal Income Fd (NNC),NNC
                    NYSE Equity,Nuveen Ohio Quality Municipal Income Fund (NUO),NUO
                    NYSE Equity,Nuveen Pennsylvania Municipal Value Fund (NPN),NPN
                    NYSE Equity,Nuveen Pennsylvania Quality Municipal Income Fund (NQP),NQP
                    NYSE Equity,Nuveen Preferred & Income Opportunities Fund (JPC),JPC
                    NYSE Equity,Nuveen Preferred & Income Securities Fund (JPS),JPS
                    NYSE Equity,Nuveen Preferred and Income 2022 Term Fund (JPT),JPT
                    NYSE Equity,Nuveen Preferred and Income Term Fund (JPI),JPI
                    NYSE Equity,Nuveen Quality Municipal Income Fund (NAD),NAD
                    NYSE Equity,Nuveen Real Asset Income and Growth Fund (JRI),JRI
                    NYSE Equity,Nuveen Real Estate Fund (JRS),JRS
                    NYSE Equity,Nuveen S&P 500 Buy-Write Income Fund (BXMX),BXMX
                    NYSE Equity,Nuveen S&P 500 Dynamic Overwrite Fund (SPXX),SPXX
                    NYSE Equity,Nuveen Select Maturities Municipal Fund (NIM),NIM
                    NYSE Equity,Nuveen Select Tax Free Income Portfolio (NXP),NXP
                    NYSE Equity,Nuveen Select Tax Free Income Portfolio II (NXQ),NXQ
                    NYSE Equity,Nuveen Select Tax Free Income Portfolio III (NXR),NXR
                    NYSE Equity,Nuveen Senior Income Fund (NSL),NSL
                    NYSE Equity,Nuveen Short Duration Credit Opportunities Fund (JSD),JSD
                    NYSE Equity,Nuveen Taxable Municipal Income Fund (NBB),NBB
                    NYSE Equity,Nuveen Tax-Advantaged Dividend Growth Fund (JTD),JTD
                    NYSE Equity,Nuveen Tax-Advantaged Total Return Strategy Fund (JTA),JTA
                    NYSE Equity,Nuveen Texas Quality Municipal Income Fund (NTX),NTX
                    NYSE Equity,Nuveen Virginia Quality Municipal Income Fund (NPV),NPV
                    NYSE Equity,Nuveenn Intermediate Duration Quality Municipal Term Fund (NIQ),NIQ
                    NYSE Equity,Nuven Mortgage Opportunity Term Fund 2 (JMT),JMT
                    NYSE Equity,nVent Electric plc (NVT),NVT
                    NYSE Equity,"NVR, Inc. (NVR)",NVR
                    NYSE Equity,"Oaktree Capital Group, LLC (OAK)",OAK
                    NYSE Equity,"Oaktree Capital Group, LLC (OAK^A)",OAK^A
                    NYSE Equity,"Oaktree Capital Group, LLC (OAK^B)",OAK^B
                    NYSE Equity,Oaktree Specialty Lending Corporation (OSLE),OSLE
                    NYSE Equity,Oasis Midstream Partners LP (OMP),OMP
                    NYSE Equity,Oasis Petroleum Inc. (OAS),OAS
                    NYSE Equity,Obsidian Energy Ltd. (OBE),OBE
                    NYSE Equity,Occidental Petroleum Corporation (OXY),OXY
                    NYSE Equity,"Oceaneering International, Inc. (OII)",OII
                    NYSE Equity,Och-Ziff Capital Management Group LLC (OZM),OZM
                    NYSE Equity,Ocwen Financial Corporation (OCN),OCN
                    NYSE Equity,OFG Bancorp (OFG),OFG
                    NYSE Equity,OFG Bancorp (OFG^A),OFG^A
                    NYSE Equity,OFG Bancorp (OFG^B),OFG^B
                    NYSE Equity,OFG Bancorp (OFG^D),OFG^D
                    NYSE Equity,OGE Energy Corp (OGE),OGE
                    NYSE Equity,Oi S.A. (OIBR.C),OIBR.C
                    NYSE Equity,"Oil States International, Inc. (OIS)",OIS
                    NYSE Equity,Oil-Dri Corporation Of America (ODC),ODC
                    NYSE Equity,Old Republic International Corporation (ORI),ORI
                    NYSE Equity,Olin Corporation (OLN),OLN
                    NYSE Equity,"Omega Healthcare Investors, Inc. (OHI)",OHI
                    NYSE Equity,Omnicom Group Inc. (OMC),OMC
                    NYSE Equity,OMNOVA Solutions Inc. (OMN),OMN
                    NYSE Equity,"On Deck Capital, Inc. (ONDK)",ONDK
                    NYSE Equity,"ONE Gas, Inc. (OGS)",OGS
                    NYSE Equity,"One Liberty Properties, Inc. (OLP)",OLP
                    NYSE Equity,"OneMain Holdings, Inc. (OMF)",OMF
                    NYSE Equity,"ONEOK, Inc. (OKE)",OKE
                    NYSE Equity,OneSmart International Education Group Limited (ONE),ONE
                    NYSE Equity,"Ooma, Inc. (OOMA)",OOMA
                    NYSE Equity,"Oppenheimer Holdings, Inc. (OPY)",OPY
                    NYSE Equity,Oracle Corporation (ORCL),ORCL
                    NYSE Equity,Orange (ORAN),ORAN
                    NYSE Equity,"Orchid Island Capital, Inc. (ORC)",ORC
                    NYSE Equity,Orion Engineered Carbons S.A (OEC),OEC
                    NYSE Equity,"Orion Group Holdings, Inc. (ORN)",ORN
                    NYSE Equity,Orix Corp Ads (IX),IX
                    NYSE Equity,"Ormat Technologies, Inc. (ORA)",ORA
                    NYSE Equity,Oshkosh Corporation (OSK),OSK
                    NYSE Equity,Osisko Gold Royalties Ltd (OR),OR
                    NYSE Equity,OUTFRONT Media Inc. (OUT),OUT
                    NYSE Equity,"Overseas Shipholding Group, Inc. (OSG)",OSG
                    NYSE Equity,"Owens & Minor, Inc. (OMI)",OMI
                    NYSE Equity,Owens Corning Inc (OC),OC
                    NYSE Equity,"Owens-Illinois, Inc. (OI)",OI
                    NYSE Equity,"Oxford Industries, Inc. (OXM)",OXM
                    NYSE Equity,Pacific Coast Oil Trust (ROYT),ROYT
                    NYSE Equity,Pacific Drilling S.A. (PACD),PACD
                    NYSE Equity,Pacific Gas & Electric Co. (PCG),PCG
                    NYSE Equity,Packaging Corporation of America (PKG),PKG
                    NYSE Equity,"PagerDuty, Inc. (PD)",PD
                    NYSE Equity,PagSeguro Digital Ltd. (PAGS),PAGS
                    NYSE Equity,"Palo Alto Networks, Inc. (PANW)",PANW
                    NYSE Equity,Pampa Energia S.A. (PAM),PAM
                    NYSE Equity,Panhandle Royalty Company (PHX),PHX
                    NYSE Equity,"Par Pacific Holdings, Inc. (PARR)",PARR
                    NYSE Equity,PAR Technology Corporation (PAR),PAR
                    NYSE Equity,"Paramount Group, Inc. (PGRE)",PGRE
                    NYSE Equity,Park Electrochemical Corporation (PKE),PKE
                    NYSE Equity,Park Hotels & Resorts Inc. (PK),PK
                    NYSE Equity,Parker Drilling Company (PKD),PKD
                    NYSE Equity,Parker-Hannifin Corporation (PH),PH
                    NYSE Equity,"Parsley Energy, Inc. (PE)",PE
                    NYSE Equity,Parsons Corporation (PSN),PSN
                    NYSE Equity,PartnerRe Ltd. (PRE^F),PRE^F
                    NYSE Equity,PartnerRe Ltd. (PRE^G),PRE^G
                    NYSE Equity,PartnerRe Ltd. (PRE^H),PRE^H
                    NYSE Equity,PartnerRe Ltd. (PRE^I),PRE^I
                    NYSE Equity,Party City Holdco Inc. (PRTY),PRTY
                    NYSE Equity,"Paycom Software, Inc. (PAYC)",PAYC
                    NYSE Equity,PBF Energy Inc. (PBF),PBF
                    NYSE Equity,PBF Logistics LP (PBFX),PBFX
                    NYSE Equity,Peabody Energy Corporation (BTU),BTU
                    NYSE Equity,"Pearson, Plc (PSO)",PSO
                    NYSE Equity,Pebblebrook Hotel Trust (PEB),PEB
                    NYSE Equity,Pebblebrook Hotel Trust (PEB^C),PEB^C
                    NYSE Equity,Pebblebrook Hotel Trust (PEB^D),PEB^D
                    NYSE Equity,Pebblebrook Hotel Trust (PEB^E),PEB^E
                    NYSE Equity,Pebblebrook Hotel Trust (PEB^F),PEB^F
                    NYSE Equity,Pembina Pipeline Corp. (PBA),PBA
                    NYSE Equity,Pennsylvania Real Estate Investment Trust (PEI),PEI
                    NYSE Equity,Pennsylvania Real Estate Investment Trust (PEI^B),PEI^B
                    NYSE Equity,Pennsylvania Real Estate Investment Trust (PEI^C),PEI^C
                    NYSE Equity,Pennsylvania Real Estate Investment Trust (PEI^D),PEI^D
                    NYSE Equity,"PennyMac Financial Services, Inc. (PFSI)",PFSI
                    NYSE Equity,PennyMac Mortgage Investment Trust (PMT),PMT
                    NYSE Equity,PennyMac Mortgage Investment Trust (PMT^A),PMT^A
                    NYSE Equity,PennyMac Mortgage Investment Trust (PMT^B),PMT^B
                    NYSE Equity,"Penske Automotive Group, Inc. (PAG)",PAG
                    NYSE Equity,Pentair plc. (PNR),PNR
                    NYSE Equity,"Penumbra, Inc. (PEN)",PEN
                    NYSE Equity,Performance Food Group Company (PFGC),PFGC
                    NYSE Equity,"PerkinElmer, Inc. (PKI)",PKI
                    NYSE Equity,Permian Basin Royalty Trust (PBT),PBT
                    NYSE Equity,Permianville Royalty Trust (PVL),PVL
                    NYSE Equity,PermRock Royalty Trust (PRT),PRT
                    NYSE Equity,Perrigo Company (PRGO),PRGO
                    NYSE Equity,Perspecta Inc. (PRSP),PRSP
                    NYSE Equity,PetroChina Company Limited (PTR),PTR
                    NYSE Equity,Petroleo Brasileiro S.A.- Petrobras (PBR),PBR
                    NYSE Equity,Petroleo Brasileiro S.A.- Petrobras (PBR.A),PBR.A
                    NYSE Equity,"Pfizer, Inc. (PFE)",PFE
                    NYSE Equity,"PGIM Global High Yield Fund, Inc. (GHY)",GHY
                    NYSE Equity,"PGIM High Yield Bond Fund, Inc. (ISD)",ISD
                    NYSE Equity,"PGT Innovations, Inc. (PGTI)",PGTI
                    NYSE Equity,Philip Morris International Inc (PM),PM
                    NYSE Equity,Phillips 66 (PSX),PSX
                    NYSE Equity,Phillips 66 Partners LP (PSXP),PSXP
                    NYSE Equity,Phoenix New Media Limited (FENG),FENG
                    NYSE Equity,Physicians Realty Trust (DOC),DOC
                    NYSE Equity,"Piedmont Office Realty Trust, Inc. (PDM)",PDM
                    NYSE Equity,"Pier 1 Imports, Inc. (PIR)",PIR
                    NYSE Equity,PIMCO California Municipal Income Fund (PCQ),PCQ
                    NYSE Equity,Pimco California Municipal Income Fund II (PCK),PCK
                    NYSE Equity,PIMCO California Municipal Income Fund III (PZC),PZC
                    NYSE Equity,"PIMCO Commercial Mortgage Securities Trust, Inc. (PCM)",PCM
                    NYSE Equity,Pimco Corporate & Income Opportunity Fund (PTY),PTY
                    NYSE Equity,Pimco Corporate & Income Stategy Fund (PCN),PCN
                    NYSE Equity,PIMCO Dynamic Credit and Mortgage Income Fund (PCI),PCI
                    NYSE Equity,PIMCO Dynamic Income Fund (PDI),PDI
                    NYSE Equity,PIMCO Energy and Tactical Credit Opportunities Fund (NRGX),NRGX
                    NYSE Equity,Pimco Global Stocksplus & Income Fund (PGP),PGP
                    NYSE Equity,Pimco High Income Fund (PHK),PHK
                    NYSE Equity,Pimco Income Opportunity Fund (PKO),PKO
                    NYSE Equity,PIMCO Income Strategy Fund (PFL),PFL
                    NYSE Equity,PIMCO Income Strategy Fund II (PFN),PFN
                    NYSE Equity,PIMCO Municipal Income Fund (PMF),PMF
                    NYSE Equity,Pimco Municipal Income Fund II (PML),PML
                    NYSE Equity,PIMCO Municipal Income Fund III (PMX),PMX
                    NYSE Equity,PIMCO New York Municipal Income Fund (PNF),PNF
                    NYSE Equity,Pimco New York Municipal Income Fund II (PNI),PNI
                    NYSE Equity,PIMCO New York Municipal Income Fund III (PYN),PYN
                    NYSE Equity,"PIMCO Strategic Income Fund, Inc. (RCS)",RCS
                    NYSE Equity,Pinnacle West Capital Corporation (PNW),PNW
                    NYSE Equity,"Pinterest, Inc. (PINS)",PINS
                    NYSE Equity,Pioneer Energy Services Corp. (PES),PES
                    NYSE Equity,Pioneer Floating Rate Trust (PHD),PHD
                    NYSE Equity,Pioneer High Income Trust (PHT),PHT
                    NYSE Equity,Pioneer Municipal High Income Advantage Trust (MAV),MAV
                    NYSE Equity,Pioneer Municipal High Income Trust (MHI),MHI
                    NYSE Equity,Pioneer Natural Resources Company (PXD),PXD
                    NYSE Equity,Piper Jaffray Companies (PJC),PJC
                    NYSE Equity,Pitney Bowes Inc. (PBI),PBI
                    NYSE Equity,Pitney Bowes Inc. (PBI^B),PBI^B
                    NYSE Equity,Pivotal Acquisition Corp. (PVT),PVT
                    NYSE Equity,Pivotal Acquisition Corp. (PVT.U),PVT.U
                    NYSE Equity,Pivotal Acquisition Corp. (PVT.WS),PVT.WS
                    NYSE Equity,"Pivotal Software, Inc. (PVTL)",PVTL
                    NYSE Equity,PJT Partners Inc. (PJT),PJT
                    NYSE Equity,"Plains All American Pipeline, L.P. (PAA)",PAA
                    NYSE Equity,"Plains Group Holdings, L.P. (PAGP)",PAGP
                    NYSE Equity,"Planet Fitness, Inc. (PLNT)",PLNT
                    NYSE Equity,"Plantronics, Inc. (PLT)",PLT
                    NYSE Equity,"PlayAGS, Inc. (AGS)",AGS
                    NYSE Equity,PLDT Inc. (PHI),PHI
                    NYSE Equity,"PNC Financial Services Group, Inc. (The) (PNC)",PNC
                    NYSE Equity,"PNC Financial Services Group, Inc. (The) (PNC^P)",PNC^P
                    NYSE Equity,"PNC Financial Services Group, Inc. (The) (PNC^Q)",PNC^Q
                    NYSE Equity,"PNM Resources, Inc. (Holding Co.) (PNM)",PNM
                    NYSE Equity,Polaris Industries Inc. (PII),PII
                    NYSE Equity,PolyOne Corporation (POL),POL
                    NYSE Equity,Portland General Electric Company (POR),POR
                    NYSE Equity,POSCO (PKX),PKX
                    NYSE Equity,"Post Holdings, Inc. (POST)",POST
                    NYSE Equity,"Postal Realty Trust, Inc. (PSTL)",PSTL
                    NYSE Equity,PPDAI Group Inc. (PPDF),PPDF
                    NYSE Equity,"PPG Industries, Inc. (PPG)",PPG
                    NYSE Equity,"PPL Capital Funding, Inc. (PPX)",PPX
                    NYSE Equity,PPL Corporation (PPL),PPL
                    NYSE Equity,PPlus Trust (PYS),PYS
                    NYSE Equity,PPlus Trust (PYT),PYT
                    NYSE Equity,PQ Group Holdings Inc. (PQG),PQG
                    NYSE Equity,Precision Drilling Corporation (PDS),PDS
                    NYSE Equity,"Preferred Apartment Communities, Inc. (APTS)",APTS
                    NYSE Equity,Prestige Consumer Healthcare Inc. (PBH),PBH
                    NYSE Equity,"Pretium Resources, Inc. (PVG)",PVG
                    NYSE Equity,"Primerica, Inc. (PRI)",PRI
                    NYSE Equity,Principal Real Estate Income Fund (PGZ),PGZ
                    NYSE Equity,"Priority Income Fund, Inc. (PRIF^A)",PRIF^A
                    NYSE Equity,"Priority Income Fund, Inc. (PRIF^B)",PRIF^B
                    NYSE Equity,"Priority Income Fund, Inc. (PRIF^C)",PRIF^C
                    NYSE Equity,"Priority Income Fund, Inc. (PRIF^D)",PRIF^D
                    NYSE Equity,ProAssurance Corporation (PRA),PRA
                    NYSE Equity,Procter & Gamble Company (The) (PG),PG
                    NYSE Equity,Progressive Corporation (The) (PGR),PGR
                    NYSE Equity,"Prologis, Inc. (PLD)",PLD
                    NYSE Equity,ProPetro Holding Corp. (PUMP),PUMP
                    NYSE Equity,"PROS Holdings, Inc. (PRO)",PRO
                    NYSE Equity,Prospect Capital Corporation (PBB),PBB
                    NYSE Equity,Prospect Capital Corporation (PBC),PBC
                    NYSE Equity,Prospect Capital Corporation (PBY),PBY
                    NYSE Equity,"Prosperity Bancshares, Inc. (PB)",PB
                    NYSE Equity,"Proto Labs, Inc. (PRLB)",PRLB
                    NYSE Equity,"Provident Financial Services, Inc (PFS)",PFS
                    NYSE Equity,"Prudential Financial, Inc. (PJH)",PJH
                    NYSE Equity,"Prudential Financial, Inc. (PRH)",PRH
                    NYSE Equity,"Prudential Financial, Inc. (PRS)",PRS
                    NYSE Equity,"Prudential Financial, Inc. (PRU)",PRU
                    NYSE Equity,Prudential Public Limited Company (PUK),PUK
                    NYSE Equity,Prudential Public Limited Company (PUK^),PUK^
                    NYSE Equity,Prudential Public Limited Company (PUK^A),PUK^A
                    NYSE Equity,"PS Business Parks, Inc. (PSB)",PSB
                    NYSE Equity,"PS Business Parks, Inc. (PSB^U)",PSB^U
                    NYSE Equity,"PS Business Parks, Inc. (PSB^V)",PSB^V
                    NYSE Equity,"PS Business Parks, Inc. (PSB^W)",PSB^W
                    NYSE Equity,"PS Business Parks, Inc. (PSB^X)",PSB^X
                    NYSE Equity,"PS Business Parks, Inc. (PSB^Y)",PSB^Y
                    NYSE Equity,"PT Telekomunikasi Indonesia, Tbk (TLK)",TLK
                    NYSE Equity,Public Service Enterprise Group Incorporated (PEG),PEG
                    NYSE Equity,Public Storage (PSA),PSA
                    NYSE Equity,Public Storage (PSA^A),PSA^A
                    NYSE Equity,Public Storage (PSA^B),PSA^B
                    NYSE Equity,Public Storage (PSA^C),PSA^C
                    NYSE Equity,Public Storage (PSA^D),PSA^D
                    NYSE Equity,Public Storage (PSA^E),PSA^E
                    NYSE Equity,Public Storage (PSA^F),PSA^F
                    NYSE Equity,Public Storage (PSA^G),PSA^G
                    NYSE Equity,Public Storage (PSA^H),PSA^H
                    NYSE Equity,Public Storage (PSA^U),PSA^U
                    NYSE Equity,Public Storage (PSA^V),PSA^V
                    NYSE Equity,Public Storage (PSA^W),PSA^W
                    NYSE Equity,Public Storage (PSA^X),PSA^X
                    NYSE Equity,Public Storage (PSA^Z.CL),PSA^Z.CL
                    NYSE Equity,"PulteGroup, Inc. (PHM)",PHM
                    NYSE Equity,"Pure Storage, Inc.  (PSTG)",PSTG
                    NYSE Equity,Putnam Managed Municipal Income Trust (PMM),PMM
                    NYSE Equity,Putnam Master Intermediate Income Trust (PIM),PIM
                    NYSE Equity,Putnam Municipal Opportunities Trust (PMO),PMO
                    NYSE Equity,Putnam Premier Income Trust (PPT),PPT
                    NYSE Equity,Puxin Limited (NEW),NEW
                    NYSE Equity,PVH Corp. (PVH),PVH
                    NYSE Equity,"Pyxus International, Inc. (PYX)",PYX
                    NYSE Equity,Pzena Investment Management Inc (PZN),PZN
                    NYSE Equity,"Q2 Holdings, Inc. (QTWO)",QTWO
                    NYSE Equity,"QEP Resources, Inc. (QEP)",QEP
                    NYSE Equity,Qiagen N.V. (QGEN),QGEN
                    NYSE Equity,"QTS Realty Trust, Inc. (QTS)",QTS
                    NYSE Equity,"QTS Realty Trust, Inc. (QTS^A)",QTS^A
                    NYSE Equity,"QTS Realty Trust, Inc. (QTS^B)",QTS^B
                    NYSE Equity,"Quad Graphics, Inc (QUAD)",QUAD
                    NYSE Equity,Quaker Chemical Corporation (KWR),KWR
                    NYSE Equity,Quanex Building Products Corporation (NX),NX
                    NYSE Equity,"Quanta Services, Inc. (PWR)",PWR
                    NYSE Equity,Qudian Inc. (QD),QD
                    NYSE Equity,Quest Diagnostics Incorporated (DGX),DGX
                    NYSE Equity,Quintana Energy Services Inc. (QES),QES
                    NYSE Equity,Quorum Health Corporation (QHC),QHC
                    NYSE Equity,Quotient Technology Inc. (QUOT),QUOT
                    NYSE Equity,"QVC, Inc. (QVCD)",QVCD
                    NYSE Equity,Qwest Corporation (CTAA),CTAA
                    NYSE Equity,Qwest Corporation (CTBB),CTBB
                    NYSE Equity,Qwest Corporation (CTDD),CTDD
                    NYSE Equity,Qwest Corporation (CTV),CTV
                    NYSE Equity,Qwest Corporation (CTY),CTY
                    NYSE Equity,Qwest Corporation (CTZ),CTZ
                    NYSE Equity,R.R. Donnelley & Sons Company (RRD),RRD
                    NYSE Equity,"Ra Medical Systems, Inc. (RMED)",RMED
                    NYSE Equity,Radian Group Inc. (RDN),RDN
                    NYSE Equity,Ralph Lauren Corporation (RL),RL
                    NYSE Equity,Range Resources Corporation (RRC),RRC
                    NYSE Equity,"Ranger Energy Services, Inc. (RNGR)",RNGR
                    NYSE Equity,Ranpak Holdings Corp (PACK),PACK
                    NYSE Equity,Ranpak Holdings Corp (PACK.WS),PACK.WS
                    NYSE Equity,"Raymond James Financial, Inc. (RJF)",RJF
                    NYSE Equity,Rayonier Advanced Materials Inc. (RYAM),RYAM
                    NYSE Equity,Rayonier Advanced Materials Inc. (RYAM^A),RYAM^A
                    NYSE Equity,Rayonier Inc. (RYN),RYN
                    NYSE Equity,Raytheon Company (RTN),RTN
                    NYSE Equity,"RE/MAX Holdings, Inc. (RMAX)",RMAX
                    NYSE Equity,Ready Capital Corporation (RC),RC
                    NYSE Equity,Ready Capital Corporation (RCA),RCA
                    NYSE Equity,Ready Capital Corporation (RCP),RCP
                    NYSE Equity,Realogy Holdings Corp. (RLGY),RLGY
                    NYSE Equity,Realty Income Corporation (O),O
                    NYSE Equity,"Red Hat, Inc. (RHT)",RHT
                    NYSE Equity,Red Lion Hotels Corporation (RLH),RLH
                    NYSE Equity,"Redwood Trust, Inc. (RWT)",RWT
                    NYSE Equity,Regal Beloit Corporation (RBC),RBC
                    NYSE Equity,Regalwood Global Energy Ltd. (RWGE),RWGE
                    NYSE Equity,Regalwood Global Energy Ltd. (RWGE.U),RWGE.U
                    NYSE Equity,Regalwood Global Energy Ltd. (RWGE.WS),RWGE.WS
                    NYSE Equity,Regional Management Corp. (RM),RM
                    NYSE Equity,Regions Financial Corporation (RF),RF
                    NYSE Equity,Regions Financial Corporation (RF^A),RF^A
                    NYSE Equity,Regions Financial Corporation (RF^B),RF^B
                    NYSE Equity,Regions Financial Corporation (RF^C),RF^C
                    NYSE Equity,Regis Corporation (RGS),RGS
                    NYSE Equity,"Reinsurance Group of America, Incorporated (RGA)",RGA
                    NYSE Equity,"Reinsurance Group of America, Incorporated (RZA)",RZA
                    NYSE Equity,"Reinsurance Group of America, Incorporated (RZB)",RZB
                    NYSE Equity,Reliance Steel & Aluminum Co. (RS),RS
                    NYSE Equity,RELX PLC (RELX),RELX
                    NYSE Equity,RenaissanceRe Holdings Ltd. (RNR),RNR
                    NYSE Equity,RenaissanceRe Holdings Ltd. (RNR^C),RNR^C
                    NYSE Equity,RenaissanceRe Holdings Ltd. (RNR^E),RNR^E
                    NYSE Equity,RenaissanceRe Holdings Ltd. (RNR^F),RNR^F
                    NYSE Equity,Renesola Ltd. (SOL),SOL
                    NYSE Equity,Renren Inc. (RENN),RENN
                    NYSE Equity,Replay Acquisition Corp. (RPLA),RPLA
                    NYSE Equity,Replay Acquisition Corp. (RPLA.U),RPLA.U
                    NYSE Equity,Replay Acquisition Corp. (RPLA.WS),RPLA.WS
                    NYSE Equity,"Republic Services, Inc. (RSG)",RSG
                    NYSE Equity,"Resideo Technologies, Inc. (REZI)",REZI
                    NYSE Equity,ResMed Inc. (RMD),RMD
                    NYSE Equity,Resolute Forest Products Inc. (RFP),RFP
                    NYSE Equity,Restaurant Brands International Inc. (QSR),QSR
                    NYSE Equity,"Retail Properties of America, Inc. (RPAI)",RPAI
                    NYSE Equity,Retail Value Inc. (RVI),RVI
                    NYSE Equity,"REV Group, Inc. (REVG)",REVG
                    NYSE Equity,"Revlon, Inc. (REV)",REV
                    NYSE Equity,"Revolve Group, Inc. (RVLV)",RVLV
                    NYSE Equity,REX American Resources Corporation (REX),REX
                    NYSE Equity,"Rexford Industrial Realty, Inc. (REXR)",REXR
                    NYSE Equity,"Rexford Industrial Realty, Inc. (REXR^A)",REXR^A
                    NYSE Equity,"Rexford Industrial Realty, Inc. (REXR^B)",REXR^B
                    NYSE Equity,Rexnord Corporation (RXN),RXN
                    NYSE Equity,Rexnord Corporation (RXN^A),RXN^A
                    NYSE Equity,RH (RH),RH
                    NYSE Equity,"Ringcentral, Inc. (RNG)",RNG
                    NYSE Equity,Rio Tinto Plc (RIO),RIO
                    NYSE Equity,Ritchie Bros. Auctioneers Incorporated (RBA),RBA
                    NYSE Equity,Rite Aid Corporation (RAD),RAD
                    NYSE Equity,RiverNorth Marketplace Lending Corporation (RMPL^),RMPL^
                    NYSE Equity,RiverNorth Marketplace Lending Corporation (RSF),RSF
                    NYSE Equity,"RiverNorth Opportunistic Municipal Income Fund, Inc. (RMI)",RMI
                    NYSE Equity,"RiverNorth Opportunities Fund, Inc. (RIV)",RIV
                    NYSE Equity,"RiverNorth/DoubleLine Strategic Opportunity Fund, Inc. (OPP)",OPP
                    NYSE Equity,RLI Corp. (RLI),RLI
                    NYSE Equity,RLJ Lodging Trust (RLJ),RLJ
                    NYSE Equity,RLJ Lodging Trust (RLJ^A),RLJ^A
                    NYSE Equity,RMG Acquisition Corp. (RMG),RMG
                    NYSE Equity,RMG Acquisition Corp. (RMG.U),RMG.U
                    NYSE Equity,RMG Acquisition Corp. (RMG.WS),RMG.WS
                    NYSE Equity,"Roadrunner Transportation Systems, Inc. (RRTS)",RRTS
                    NYSE Equity,"Roan Resources, Inc. (ROAN)",ROAN
                    NYSE Equity,Robert Half International Inc. (RHI),RHI
                    NYSE Equity,"Rockwell Automation, Inc. (ROK)",ROK
                    NYSE Equity,"Rogers Communication, Inc. (RCI)",RCI
                    NYSE Equity,Rogers Corporation (ROG),ROG
                    NYSE Equity,"Rollins, Inc. (ROL)",ROL
                    NYSE Equity,"Roper Technologies, Inc. (ROP)",ROP
                    NYSE Equity,Rosetta Stone (RST),RST
                    NYSE Equity,Royal Bank Of Canada (RY),RY
                    NYSE Equity,Royal Bank Of Canada (RY^T),RY^T
                    NYSE Equity,Royal Bank Scotland plc (The) (RBS),RBS
                    NYSE Equity,Royal Caribbean Cruises Ltd. (RCL),RCL
                    NYSE Equity,Royal Dutch Shell PLC (RDS.A),RDS.A
                    NYSE Equity,Royal Dutch Shell PLC (RDS.B),RDS.B
                    NYSE Equity,"Royce Global Value Trust, Inc. (RGT)",RGT
                    NYSE Equity,"Royce Micro-Cap Trust, Inc. (RMT)",RMT
                    NYSE Equity,"Royce Value Trust, Inc. (RVT)",RVT
                    NYSE Equity,"RPC, Inc. (RES)",RES
                    NYSE Equity,RPM International Inc. (RPM),RPM
                    NYSE Equity,RPT Realty (RPT),RPT
                    NYSE Equity,RPT Realty (RPT^D),RPT^D
                    NYSE Equity,"RTW Retailwinds, Inc. (RTW)",RTW
                    NYSE Equity,"Rudolph Technologies, Inc. (RTEC)",RTEC
                    NYSE Equity,"RYB Education, Inc. (RYB)",RYB
                    NYSE Equity,"Ryder System, Inc. (R)",R
                    NYSE Equity,Ryerson Holding Corporation (RYI),RYI
                    NYSE Equity,"Ryman Hospitality Properties, Inc. (RHP)",RHP
                    NYSE Equity,S&P Global Inc. (SPGI),SPGI
                    NYSE Equity,Sabine Royalty Trust (SBR),SBR
                    NYSE Equity,"Safe Bulkers, Inc (SB)",SB
                    NYSE Equity,"Safe Bulkers, Inc (SB^C)",SB^C
                    NYSE Equity,"Safe Bulkers, Inc (SB^D)",SB^D
                    NYSE Equity,"Safeguard Scientifics, Inc. (SFE)",SFE
                    NYSE Equity,Safehold Inc. (SAFE),SAFE
                    NYSE Equity,"SailPoint Technologies Holdings, Inc. (SAIL)",SAIL
                    NYSE Equity,Salesforce.com Inc (CRM),CRM
                    NYSE Equity,Salient Midstream & MLP Fund (SMM),SMM
                    NYSE Equity,"Sally Beauty Holdings, Inc. (SBH)",SBH
                    NYSE Equity,San Juan Basin Royalty Trust (SJT),SJT
                    NYSE Equity,"SandRidge Energy, Inc. (SD)",SD
                    NYSE Equity,SandRidge Mississippian Trust I (SDT),SDT
                    NYSE Equity,SandRidge Mississippian Trust II (SDR),SDR
                    NYSE Equity,SandRidge Permian Trust (PER),PER
                    NYSE Equity,Santander Consumer USA Holdings Inc. (SC),SC
                    NYSE Equity,SAP SE (SAP),SAP
                    NYSE Equity,Saratoga Investment Corp (SAB),SAB
                    NYSE Equity,Saratoga Investment Corp (SAF),SAF
                    NYSE Equity,Saratoga Investment Corp (SAR),SAR
                    NYSE Equity,Sasol Ltd. (SSL),SSL
                    NYSE Equity,"Saul Centers, Inc. (BFS)",BFS
                    NYSE Equity,"Saul Centers, Inc. (BFS^C)",BFS^C
                    NYSE Equity,"Saul Centers, Inc. (BFS^D)",BFS^D
                    NYSE Equity,Schlumberger N.V. (SLB),SLB
                    NYSE Equity,"Schneider National, Inc. (SNDR)",SNDR
                    NYSE Equity,"Schweitzer-Mauduit International, Inc. (SWM)",SWM
                    NYSE Equity,SCIENCE APPLICATIONS INTERNATIONAL CORPORATION (SAIC),SAIC
                    NYSE Equity,Scorpio Bulkers Inc. (SALT),SALT
                    NYSE Equity,Scorpio Bulkers Inc. (SLTB),SLTB
                    NYSE Equity,Scorpio Tankers Inc. (SBNA),SBNA
                    NYSE Equity,Scorpio Tankers Inc. (STNG),STNG
                    NYSE Equity,Scotts Miracle-Gro Company (The) (SMG),SMG
                    NYSE Equity,Scudder Municiple Income Trust (KTF),KTF
                    NYSE Equity,Scudder Strategic Municiple Income Trust (KSM),KSM
                    NYSE Equity,Scully Royalty Ltd. (SRL),SRL
                    NYSE Equity,Sea Limited (SE),SE
                    NYSE Equity,"Seabridge Gold, Inc. (SA)",SA
                    NYSE Equity,"SEACOR Holdings, Inc. (CKH)",CKH
                    NYSE Equity,SEACOR Marine Holdings Inc. (SMHI),SMHI
                    NYSE Equity,Seadrill Limited (SDRL),SDRL
                    NYSE Equity,Seadrill Partners LLC (SDLP),SDLP
                    NYSE Equity,Sealed Air Corporation (SEE),SEE
                    NYSE Equity,Seaspan Corporation (SSW),SSW
                    NYSE Equity,Seaspan Corporation (SSW^D),SSW^D
                    NYSE Equity,Seaspan Corporation (SSW^E),SSW^E
                    NYSE Equity,Seaspan Corporation (SSW^G),SSW^G
                    NYSE Equity,Seaspan Corporation (SSW^H),SSW^H
                    NYSE Equity,Seaspan Corporation (SSW^I),SSW^I
                    NYSE Equity,Seaspan Corporation (SSWA),SSWA
                    NYSE Equity,"SeaWorld Entertainment, Inc. (SEAS)",SEAS
                    NYSE Equity,Select Asset Inc. (JBN),JBN
                    NYSE Equity,Select Asset Inc. (JBR),JBR
                    NYSE Equity,"Select Energy Services, Inc. (WTTR)",WTTR
                    NYSE Equity,Select Medical Holdings Corporation (SEM),SEM
                    NYSE Equity,Semgroup Corporation (SEMG),SEMG
                    NYSE Equity,Sempra Energy (SRE),SRE
                    NYSE Equity,Sempra Energy (SRE^A),SRE^A
                    NYSE Equity,Sempra Energy (SRE^B),SRE^B
                    NYSE Equity,Sensata Technologies Holding plc (ST),ST
                    NYSE Equity,Sensient Technologies Corporation (SXT),SXT
                    NYSE Equity,Sequans Communications S.A. (SQNS),SQNS
                    NYSE Equity,Seritage Growth Properties (SRG),SRG
                    NYSE Equity,Seritage Growth Properties (SRG^A),SRG^A
                    NYSE Equity,Service Corporation International (SCI),SCI
                    NYSE Equity,"ServiceMaster Global Holdings, Inc. (SERV)",SERV
                    NYSE Equity,"ServiceNow, Inc. (NOW)",NOW
                    NYSE Equity,"Shake Shack, Inc. (SHAK)",SHAK
                    NYSE Equity,Shaw Communications Inc. (SJR),SJR
                    NYSE Equity,"Shell Midstream Partners, L.P. (SHLX)",SHLX
                    NYSE Equity,Sherwin-Williams Company (The) (SHW),SHW
                    NYSE Equity,Shinhan Financial Group Co Ltd (SHG),SHG
                    NYSE Equity,Ship Finance International Limited (SFL),SFL
                    NYSE Equity,Shopify Inc. (SHOP),SHOP
                    NYSE Equity,"Shutterstock, Inc. (SSTK)",SSTK
                    NYSE Equity,Sibanye Gold Limited (SBGL),SBGL
                    NYSE Equity,Signet Jewelers Limited (SIG),SIG
                    NYSE Equity,"SilverBow Resorces, Inc. (SBOW)",SBOW
                    NYSE Equity,"Simon Property Group, Inc. (SPG)",SPG
                    NYSE Equity,"Simon Property Group, Inc. (SPG^J)",SPG^J
                    NYSE Equity,"Simpson Manufacturing Company, Inc. (SSD)",SSD
                    NYSE Equity,"SINOPEC Shangai Petrochemical Company, Ltd. (SHI)",SHI
                    NYSE Equity,SITE Centers Corp. (SITC),SITC
                    NYSE Equity,SITE Centers Corp. (SITC^A),SITC^A
                    NYSE Equity,SITE Centers Corp. (SITC^J),SITC^J
                    NYSE Equity,SITE Centers Corp. (SITC^K),SITC^K
                    NYSE Equity,"SiteOne Landscape Supply, Inc. (SITE)",SITE
                    NYSE Equity,Six Flags Entertainment Corporation New (SIX),SIX
                    NYSE Equity,SJW Group (SJW),SJW
                    NYSE Equity,"SK Telecom Co., Ltd. (SKM)",SKM
                    NYSE Equity,"Skechers U.S.A., Inc. (SKX)",SKX
                    NYSE Equity,Skyline Champion Corporation (SKY),SKY
                    NYSE Equity,SL Green Realty Corp (SLG),SLG
                    NYSE Equity,SL Green Realty Corp (SLG^I),SLG^I
                    NYSE Equity,"Slack Technologies, Inc. (WORK)",WORK
                    NYSE Equity,SM Energy Company (SM),SM
                    NYSE Equity,Smartsheet Inc. (SMAR),SMAR
                    NYSE Equity,"Smith & Nephew SNATS, Inc. (SNN)",SNN
                    NYSE Equity,Snap Inc. (SNAP),SNAP
                    NYSE Equity,Snap-On Incorporated (SNA),SNA
                    NYSE Equity,Social Capital Hedosophia Holdings Corp. (IPOA),IPOA
                    NYSE Equity,Social Capital Hedosophia Holdings Corp. (IPOA.U),IPOA.U
                    NYSE Equity,Social Capital Hedosophia Holdings Corp. (IPOA.WS),IPOA.WS
                    NYSE Equity,Sociedad Quimica y Minera S.A. (SQM),SQM
                    NYSE Equity,Sogou Inc. (SOGO),SOGO
                    NYSE Equity,"Solaris Oilfield Infrastructure, Inc. (SOI)",SOI
                    NYSE Equity,SolarWinds Corporation (SWI),SWI
                    NYSE Equity,"Sonic Automotive, Inc. (SAH)",SAH
                    NYSE Equity,Sonoco Products Company (SON),SON
                    NYSE Equity,Sony Corp Ord (SNE),SNE
                    NYSE Equity,Sotheby&#39;s (BID),BID
                    NYSE Equity,"Source Capital, Inc. (SOR)",SOR
                    NYSE Equity,"South Jersey Industries, Inc. (SJI)",SJI
                    NYSE Equity,"South Jersey Industries, Inc. (SJIU)",SJIU
                    NYSE Equity,Southern California Edison Company (SCE^G),SCE^G
                    NYSE Equity,Southern California Edison Company (SCE^H),SCE^H
                    NYSE Equity,Southern California Edison Company (SCE^J),SCE^J
                    NYSE Equity,Southern California Edison Company (SCE^K),SCE^K
                    NYSE Equity,Southern California Edison Company (SCE^L),SCE^L
                    NYSE Equity,Southern Company (The) (SO),SO
                    NYSE Equity,Southern Company (The) (SOJA),SOJA
                    NYSE Equity,Southern Company (The) (SOJB),SOJB
                    NYSE Equity,Southern Company (The) (SOJC),SOJC
                    NYSE Equity,Southern Copper Corporation (SCCO),SCCO
                    NYSE Equity,Southwest Airlines Company (LUV),LUV
                    NYSE Equity,"Southwest Gas Holdings, Inc. (SWX)",SWX
                    NYSE Equity,Southwestern Energy Company (SWN),SWN
                    NYSE Equity,Spartan Energy Acquisition Corp (SPAQ),SPAQ
                    NYSE Equity,Spartan Energy Acquisition Corp (SPAQ.U),SPAQ.U
                    NYSE Equity,Spartan Energy Acquisition Corp (SPAQ.WS),SPAQ.WS
                    NYSE Equity,Special Opportunities Fund Inc. (SPE),SPE
                    NYSE Equity,Special Opportunities Fund Inc. (SPE^B),SPE^B
                    NYSE Equity,"Spectrum Brands Holdings, Inc. (SPB           )",SPB           
                    NYSE Equity,"Speedway Motorsports, Inc. (TRK)",TRK
                    NYSE Equity,Spire Inc. (SR),SR
                    NYSE Equity,Spire Inc. (SR^A),SR^A
                    NYSE Equity,"Spirit Aerosystems Holdings, Inc. (SPR)",SPR
                    NYSE Equity,"Spirit Airlines, Inc. (SAVE)",SAVE
                    NYSE Equity,Spirit MTA REIT (SMTA),SMTA
                    NYSE Equity,"Spirit Realty Capital, Inc. (SRC)",SRC
                    NYSE Equity,"Spirit Realty Capital, Inc. (SRC^A)",SRC^A
                    NYSE Equity,Spotify Technology S.A. (SPOT),SPOT
                    NYSE Equity,Sprague Resources LP (SRLP),SRLP
                    NYSE Equity,Sprint Corporation (S),S
                    NYSE Equity,SPX Corporation (SPXC),SPXC
                    NYSE Equity,"SPX FLOW, Inc. (FLOW)",FLOW
                    NYSE Equity,"Square, Inc. (SQ)",SQ
                    NYSE Equity,St. Joe Company (The) (JOE),JOE
                    NYSE Equity,"Stag Industrial, Inc. (STAG)",STAG
                    NYSE Equity,"Stag Industrial, Inc. (STAG^C)",STAG^C
                    NYSE Equity,"Stage Stores, Inc. (SSI)",SSI
                    NYSE Equity,"Standard Motor Products, Inc. (SMP)",SMP
                    NYSE Equity,Standex International Corporation (SXI),SXI
                    NYSE Equity,"Stanley Black & Decker, Inc. (SWJ)",SWJ
                    NYSE Equity,"Stanley Black & Decker, Inc. (SWK)",SWK
                    NYSE Equity,"Stanley Black & Decker, Inc. (SWP)",SWP
                    NYSE Equity,Stantec Inc (STN),STN
                    NYSE Equity,"Star Group, L.P. (SGU)",SGU
                    NYSE Equity,"StarTek, Inc. (SRT)",SRT
                    NYSE Equity,"STARWOOD PROPERTY TRUST, INC. (STWD)",STWD
                    NYSE Equity,State Street Corporation (STT),STT
                    NYSE Equity,State Street Corporation (STT^C),STT^C
                    NYSE Equity,State Street Corporation (STT^D),STT^D
                    NYSE Equity,State Street Corporation (STT^E),STT^E
                    NYSE Equity,State Street Corporation (STT^G),STT^G
                    NYSE Equity,Steel Partners Holdings LP (SPLP),SPLP
                    NYSE Equity,Steel Partners Holdings LP (SPLP^A),SPLP^A
                    NYSE Equity,Steelcase Inc. (SCS),SCS
                    NYSE Equity,Stellus Capital Investment Corporation (SCA),SCA
                    NYSE Equity,Stellus Capital Investment Corporation (SCM),SCM
                    NYSE Equity,Stepan Company (SCL),SCL
                    NYSE Equity,STERIS plc (STE),STE
                    NYSE Equity,Sterling Bancorp (STL),STL
                    NYSE Equity,Sterling Bancorp (STL^A),STL^A
                    NYSE Equity,Stewart Information Services Corporation (STC),STC
                    NYSE Equity,Stifel Financial Corporation (SF),SF
                    NYSE Equity,Stifel Financial Corporation (SF^A),SF^A
                    NYSE Equity,Stifel Financial Corporation (SF^B),SF^B
                    NYSE Equity,Stifel Financial Corporation (SFB),SFB
                    NYSE Equity,STMicroelectronics N.V. (STM),STM
                    NYSE Equity,Stone Harbor Emerging Markets Income Fund (EDF),EDF
                    NYSE Equity,Stone Harbor Emerging Markets Total Income Fund (EDI),EDI
                    NYSE Equity,StoneMor Partners L.P. (STON),STON
                    NYSE Equity,"Stoneridge, Inc. (SRI)",SRI
                    NYSE Equity,STORE Capital Corporation (STOR),STOR
                    NYSE Equity,STRATS Trust (GJH),GJH
                    NYSE Equity,STRATS Trust (GJO),GJO
                    NYSE Equity,STRATS Trust (GJS),GJS
                    NYSE Equity,Stryker Corporation (SYK),SYK
                    NYSE Equity,Studio City International Holdings Limited (MSC),MSC
                    NYSE Equity,"Sturm, Ruger & Company, Inc. (RGR)",RGR
                    NYSE Equity,"Suburban Propane Partners, L.P. (SPH)",SPH
                    NYSE Equity,Sumitomo Mitsui Financial Group Inc (SMFG),SMFG
                    NYSE Equity,"Summit Hotel Properties, Inc. (INN)",INN
                    NYSE Equity,"Summit Hotel Properties, Inc. (INN^D)",INN^D
                    NYSE Equity,"Summit Hotel Properties, Inc. (INN^E)",INN^E
                    NYSE Equity,"Summit Materials, Inc. (SUM)",SUM
                    NYSE Equity,"Summit Midstream Partners, LP (SMLP)",SMLP
                    NYSE Equity,"Sun Communities, Inc. (SUI)",SUI
                    NYSE Equity,Sun Life Financial Inc. (SLF),SLF
                    NYSE Equity,"SunCoke Energy Partners, L.P. (SXCP)",SXCP
                    NYSE Equity,"SunCoke Energy, Inc. (SXC)",SXC
                    NYSE Equity,Suncor Energy  Inc. (SU),SU
                    NYSE Equity,Sunlands Technology Group (STG),STG
                    NYSE Equity,Sunoco LP (SUN),SUN
                    NYSE Equity,"Sunstone Hotel Investors, Inc. (SHO)",SHO
                    NYSE Equity,"Sunstone Hotel Investors, Inc. (SHO^E)",SHO^E
                    NYSE Equity,"Sunstone Hotel Investors, Inc. (SHO^F)",SHO^F
                    NYSE Equity,"SunTrust Banks, Inc. (STI)",STI
                    NYSE Equity,"SunTrust Banks, Inc. (STI^A)",STI^A
                    NYSE Equity,"Superior Energy Services, Inc. (SPN)",SPN
                    NYSE Equity,"Superior Industries International, Inc. (SUP)",SUP
                    NYSE Equity,Suzano S.A. (SUZ),SUZ
                    NYSE Equity,"Swiss Helvetia Fund, Inc. (The) (SWZ)",SWZ
                    NYSE Equity,"Switch, Inc. (SWCH)",SWCH
                    NYSE Equity,Synchrony Financial (SYF),SYF
                    NYSE Equity,Synnex Corporation (SNX),SNX
                    NYSE Equity,Synovus Financial Corp. (SNV),SNV
                    NYSE Equity,Synovus Financial Corp. (SNV^D),SNV^D
                    NYSE Equity,"Synthetic Fixed-Income Securities, Inc. (GJP)",GJP
                    NYSE Equity,"Synthetic Fixed-Income Securities, Inc. (GJR)",GJR
                    NYSE Equity,"Synthetic Fixed-Income Securities, Inc. (GJT)",GJT
                    NYSE Equity,"Synthetic Fixed-Income Securities, Inc. (GJV)",GJV
                    NYSE Equity,Sysco Corporation (SYY),SYY
                    NYSE Equity,Systemax Inc. (SYX),SYX
                    NYSE Equity,"Tableau Software, Inc. (DATA)",DATA
                    NYSE Equity,"Tailored Brands, Inc. (TLRD)",TLRD
                    NYSE Equity,"Taiwan Fund, Inc. (The) (TWN)",TWN
                    NYSE Equity,Taiwan Semiconductor Manufacturing Company Ltd. (TSM),TSM
                    NYSE Equity,Takeda Pharmaceutical Company Limited (TAK),TAK
                    NYSE Equity,TAL Education Group (TAL),TAL
                    NYSE Equity,"Tallgrass Energy, LP (TGE)",TGE
                    NYSE Equity,"Talos Energy, Inc. (TALO)",TALO
                    NYSE Equity,"Tanger Factory Outlet Centers, Inc. (SKT)",SKT
                    NYSE Equity,"Tapestry, Inc. (TPR)",TPR
                    NYSE Equity,Targa Resources Partners LP (NGLS^A),NGLS^A
                    NYSE Equity,"Targa Resources, Inc. (TRGP)",TRGP
                    NYSE Equity,Target Corporation (TGT),TGT
                    NYSE Equity,Taro Pharmaceutical Industries Ltd. (TARO),TARO
                    NYSE Equity,Tata Motors Ltd (TTM),TTM
                    NYSE Equity,"Taubman Centers, Inc. (TCO)",TCO
                    NYSE Equity,"Taubman Centers, Inc. (TCO^J)",TCO^J
                    NYSE Equity,"Taubman Centers, Inc. (TCO^K)",TCO^K
                    NYSE Equity,Taylor Morrison Home Corporation (TMHC),TMHC
                    NYSE Equity,TC Energy Corporation (TRP),TRP
                    NYSE Equity,"TC PipeLines, LP (TCP)",TCP
                    NYSE Equity,TCF Financial Corporation (TCF),TCF
                    NYSE Equity,TCF Financial Corporation (TCF^D),TCF^D
                    NYSE Equity,"TCW Strategic Income Fund, Inc. (TSI)",TSI
                    NYSE Equity,TE Connectivity Ltd. (TEL),TEL
                    NYSE Equity,"Team, Inc. (TISI)",TISI
                    NYSE Equity,TechnipFMC plc (FTI),FTI
                    NYSE Equity,Teck Resources Ltd (TECK),TECK
                    NYSE Equity,Teekay Corporation (TK),TK
                    NYSE Equity,Teekay LNG Partners L.P. (TGP),TGP
                    NYSE Equity,Teekay LNG Partners L.P. (TGP^A),TGP^A
                    NYSE Equity,Teekay LNG Partners L.P. (TGP^B),TGP^B
                    NYSE Equity,Teekay Offshore Partners L.P. (TOO),TOO
                    NYSE Equity,Teekay Offshore Partners L.P. (TOO^A),TOO^A
                    NYSE Equity,Teekay Offshore Partners L.P. (TOO^B),TOO^B
                    NYSE Equity,Teekay Offshore Partners L.P. (TOO^E),TOO^E
                    NYSE Equity,Teekay Tankers Ltd. (TNK),TNK
                    NYSE Equity,TEGNA Inc. (GCI),GCI
                    NYSE Equity,TEGNA Inc. (TGNA),TGNA
                    NYSE Equity,Tejon Ranch Co (TRC),TRC
                    NYSE Equity,Tekla Healthcare Investors (HQH),HQH
                    NYSE Equity,Tekla Healthcare Opportunies Fund (THQ),THQ
                    NYSE Equity,Tekla Life Sciences Investors (HQL),HQL
                    NYSE Equity,Tekla World Healthcare Fund (THW),THW
                    NYSE Equity,"Teladoc Health, Inc. (TDOC)",TDOC
                    NYSE Equity,"Telaria, Inc. (TLRA)",TLRA
                    NYSE Equity,Telecom Argentina Stet - France Telecom S.A. (TEO),TEO
                    NYSE Equity,Telecom Italia S.P.A. (TI),TI
                    NYSE Equity,Telecom Italia S.P.A. (TI.A),TI.A
                    NYSE Equity,Teledyne Technologies Incorporated (TDY),TDY
                    NYSE Equity,Teleflex Incorporated (TFX),TFX
                    NYSE Equity,Telefonica Brasil S.A. (VIV),VIV
                    NYSE Equity,Telefonica SA (TEF),TEF
                    NYSE Equity,"Telephone and Data Systems, Inc. (TDA)",TDA
                    NYSE Equity,"Telephone and Data Systems, Inc. (TDE)",TDE
                    NYSE Equity,"Telephone and Data Systems, Inc. (TDI)",TDI
                    NYSE Equity,"Telephone and Data Systems, Inc. (TDJ)",TDJ
                    NYSE Equity,"Telephone and Data Systems, Inc. (TDS)",TDS
                    NYSE Equity,TELUS Corporation (TU),TU
                    NYSE Equity,"Templeton Dragon Fund, Inc. (TDF)",TDF
                    NYSE Equity,Templeton Emerging Markets Fund (EMF),EMF
                    NYSE Equity,"Templeton Emerging Markets Income Fund, Inc. (TEI)",TEI
                    NYSE Equity,"Templeton Global Income Fund, Inc. (GIM)",GIM
                    NYSE Equity,"Tempur Sealy International, Inc. (TPX)",TPX
                    NYSE Equity,Tenaris S.A. (TS),TS
                    NYSE Equity,Tencent Music Entertainment Group (TME),TME
                    NYSE Equity,Tenet Healthcare Corporation (THC),THC
                    NYSE Equity,Tennant Company (TNC),TNC
                    NYSE Equity,Tenneco Inc. (TEN),TEN
                    NYSE Equity,Tennessee Valley Authority (TVC),TVC
                    NYSE Equity,Tennessee Valley Authority (TVE),TVE
                    NYSE Equity,Teradata Corporation (TDC),TDC
                    NYSE Equity,Terex Corporation (TEX),TEX
                    NYSE Equity,Ternium S.A. (TX),TX
                    NYSE Equity,Terreno Realty Corporation (TRNO),TRNO
                    NYSE Equity,"Tetra Technologies, Inc. (TTI)",TTI
                    NYSE Equity,Teva Pharmaceutical Industries Limited (TEVA),TEVA
                    NYSE Equity,Texas Pacific Land Trust (TPL),TPL
                    NYSE Equity,Textainer Group Holdings Limited (TGH),TGH
                    NYSE Equity,Textron Inc. (TXT),TXT
                    NYSE Equity,The AES Corporation (AES),AES
                    NYSE Equity,The Blackstone Group L.P. (BX),BX
                    NYSE Equity,"The Central and Eastern Europe Fund, Inc. (CEE)",CEE
                    NYSE Equity,The Charles Schwab Corporation (SCHW),SCHW
                    NYSE Equity,The Charles Schwab Corporation (SCHW^C),SCHW^C
                    NYSE Equity,The Charles Schwab Corporation (SCHW^D),SCHW^D
                    NYSE Equity,"The Cooper Companies, Inc.  (COO)",COO
                    NYSE Equity,The Gabelli Dividend & Income Trust (GDV),GDV
                    NYSE Equity,The Gabelli Dividend & Income Trust (GDV^A),GDV^A
                    NYSE Equity,The Gabelli Dividend & Income Trust (GDV^D),GDV^D
                    NYSE Equity,The Gabelli Dividend & Income Trust (GDV^G),GDV^G
                    NYSE Equity,The Gabelli Dividend & Income Trust (GDV^H),GDV^H
                    NYSE Equity,The Gabelli Healthcare & Wellness Trust (GRX),GRX
                    NYSE Equity,The Gabelli Healthcare & Wellness Trust (GRX^A),GRX^A
                    NYSE Equity,The Gabelli Healthcare & Wellness Trust (GRX^B),GRX^B
                    NYSE Equity,The GDL Fund (GDL),GDL
                    NYSE Equity,The GDL Fund (GDL^C),GDL^C
                    NYSE Equity,"The Hanover Insurance Group, Inc. (THG)",THG
                    NYSE Equity,"The Hanover Insurance Group, Inc. (THGA)",THGA
                    NYSE Equity,The Madison Square Garden Company (MSG),MSG
                    NYSE Equity,"The Rubicon Project, Inc. (RUBI)",RUBI
                    NYSE Equity,"The Travelers Companies, Inc. (TRV)",TRV
                    NYSE Equity,The Vivaldi Opportunities Fund (VAM),VAM
                    NYSE Equity,Thermo Fisher Scientific Inc (TMO),TMO
                    NYSE Equity,"Thermon Group Holdings, Inc. (THR)",THR
                    NYSE Equity,Third Point Reinsurance Ltd. (TPRE),TPRE
                    NYSE Equity,THL Credit Senior Loan Fund (TSLF),TSLF
                    NYSE Equity,"THL Credit, Inc. (TCRW)",TCRW
                    NYSE Equity,"THL Credit, Inc. (TCRZ)",TCRZ
                    NYSE Equity,Thomson Reuters Corp (TRI),TRI
                    NYSE Equity,"Thor Industries, Inc. (THO)",THO
                    NYSE Equity,Tidewater Inc. (TDW),TDW
                    NYSE Equity,Tidewater Inc. (TDW.WS.A),TDW.WS.A
                    NYSE Equity,Tidewater Inc. (TDW.WS.B),TDW.WS.B
                    NYSE Equity,Tiffany & Co. (TIF),TIF
                    NYSE Equity,"Tilly&#39;s, Inc. (TLYS)",TLYS
                    NYSE Equity,TIM Participacoes S.A. (TSU),TSU
                    NYSE Equity,Timken Company (The) (TKR),TKR
                    NYSE Equity,TimkenSteel Corporation (TMST),TMST
                    NYSE Equity,"Titan International, Inc. (TWI)",TWI
                    NYSE Equity,"TJX Companies, Inc. (The) (TJX)",TJX
                    NYSE Equity,"Toll Brothers, Inc. (TOL)",TOL
                    NYSE Equity,"Tootsie Roll Industries, Inc. (TR)",TR
                    NYSE Equity,TopBuild Corp. (BLD),BLD
                    NYSE Equity,Torchmark Corporation (TMK),TMK
                    NYSE Equity,Torchmark Corporation (TMK^C),TMK^C
                    NYSE Equity,Toro Company (The) (TTC),TTC
                    NYSE Equity,Toronto Dominion Bank (The) (TD),TD
                    NYSE Equity,Tortoise Acquisition Corp. (SHLL),SHLL
                    NYSE Equity,Tortoise Acquisition Corp. (SHLL.U),SHLL.U
                    NYSE Equity,Tortoise Acquisition Corp. (SHLL.WS),SHLL.WS
                    NYSE Equity,"Tortoise Energy Independence Fund, Inc. (NDP)",NDP
                    NYSE Equity,Tortoise Energy Infrastructure Corporation (TYG),TYG
                    NYSE Equity,Tortoise Essential Assets Income Term Fund (TEAF),TEAF
                    NYSE Equity,"Tortoise Midstream Energy Fund, Inc. (NTG)",NTG
                    NYSE Equity,"Tortoise Pipeline & Energy Fund, Inc. (TTP)",TTP
                    NYSE Equity,"Tortoise Power and Energy Infrastructure Fund, Inc (TPZ)",TPZ
                    NYSE Equity,Total S.A. (TOT),TOT
                    NYSE Equity,"Total System Services, Inc. (TSS)",TSS
                    NYSE Equity,"Tower International, Inc. (TOWR)",TOWR
                    NYSE Equity,"Townsquare Media, Inc. (TSQ)",TSQ
                    NYSE Equity,Toyota Motor Corp Ltd Ord (TM),TM
                    NYSE Equity,TPG Pace Holdings Corp. (TPGH),TPGH
                    NYSE Equity,TPG Pace Holdings Corp. (TPGH.U),TPGH.U
                    NYSE Equity,TPG Pace Holdings Corp. (TPGH.WS),TPGH.WS
                    NYSE Equity,"TPG RE Finance Trust, Inc. (TRTX)",TRTX
                    NYSE Equity,"TPG Specialty Lending, Inc. (TSLX)",TSLX
                    NYSE Equity,TransAlta Corporation (TAC),TAC
                    NYSE Equity,"Transcontinental Realty Investors, Inc. (TCI)",TCI
                    NYSE Equity,Transdigm Group Incorporated (TDG),TDG
                    NYSE Equity,Transocean Ltd. (RIG),RIG
                    NYSE Equity,Transportadora De Gas Sa Ord B (TGS),TGS
                    NYSE Equity,TransUnion (TRU),TRU
                    NYSE Equity,Trecora Resources (TREC),TREC
                    NYSE Equity,Tredegar Corporation (TG),TG
                    NYSE Equity,"Treehouse Foods, Inc. (THS)",THS
                    NYSE Equity,"Trex Company, Inc. (TREX)",TREX
                    NYSE Equity,Tri Continental Corporation (TY),TY
                    NYSE Equity,Tri Continental Corporation (TY^),TY^
                    NYSE Equity,"TRI Pointe Group, Inc. (TPH)",TPH
                    NYSE Equity,Tribune Media Company (TRCO),TRCO
                    NYSE Equity,Trine Acquisition Corp. (TRNE),TRNE
                    NYSE Equity,Trine Acquisition Corp. (TRNE.U),TRNE.U
                    NYSE Equity,Trine Acquisition Corp. (TRNE.WS),TRNE.WS
                    NYSE Equity,"TriNet Group, Inc. (TNET)",TNET
                    NYSE Equity,"Trinity Industries, Inc. (TRN)",TRN
                    NYSE Equity,Trinseo S.A. (TSE),TSE
                    NYSE Equity,TriplePoint Venture Growth BDC Corp. (TPVG),TPVG
                    NYSE Equity,TriplePoint Venture Growth BDC Corp. (TPVY),TPVY
                    NYSE Equity,Triple-S Management Corporation (GTS),GTS
                    NYSE Equity,Triton International Limited (TRTN),TRTN
                    NYSE Equity,Triton International Limited (TRTN^A),TRTN^A
                    NYSE Equity,"Triumph Group, Inc. (TGI)",TGI
                    NYSE Equity,Tronox Holdings plc (TROX),TROX
                    NYSE Equity,"TrueBlue, Inc. (TBI)",TBI
                    NYSE Equity,Tsakos Energy Navigation Ltd (TNP),TNP
                    NYSE Equity,Tsakos Energy Navigation Ltd (TNP^B),TNP^B
                    NYSE Equity,Tsakos Energy Navigation Ltd (TNP^C),TNP^C
                    NYSE Equity,Tsakos Energy Navigation Ltd (TNP^D),TNP^D
                    NYSE Equity,Tsakos Energy Navigation Ltd (TNP^E),TNP^E
                    NYSE Equity,Tsakos Energy Navigation Ltd (TNP^F),TNP^F
                    NYSE Equity,Tufin Software Technologies Ltd. (TUFN),TUFN
                    NYSE Equity,Tupperware Brands Corporation (TUP),TUP
                    NYSE Equity,Turkcell Iletisim Hizmetleri AS (TKC),TKC
                    NYSE Equity,"Turning Point Brands, Inc. (TPB)",TPB
                    NYSE Equity,Turquoise Hill Resources Ltd. (TRQ),TRQ
                    NYSE Equity,Tutor Perini Corporation (TPC),TPC
                    NYSE Equity,Twilio Inc. (TWLO),TWLO
                    NYSE Equity,"Twin River Worldwide Holdings, Inc. (TRWH)",TRWH
                    NYSE Equity,"Twitter, Inc. (TWTR)",TWTR
                    NYSE Equity,Two Harbors Investments Corp (TWO),TWO
                    NYSE Equity,Two Harbors Investments Corp (TWO^A),TWO^A
                    NYSE Equity,Two Harbors Investments Corp (TWO^B),TWO^B
                    NYSE Equity,Two Harbors Investments Corp (TWO^C),TWO^C
                    NYSE Equity,Two Harbors Investments Corp (TWO^D),TWO^D
                    NYSE Equity,Two Harbors Investments Corp (TWO^E),TWO^E
                    NYSE Equity,"Tyler Technologies, Inc. (TYL)",TYL
                    NYSE Equity,"Tyson Foods, Inc. (TSN)",TSN
                    NYSE Equity,U.S. Bancorp (USB),USB
                    NYSE Equity,U.S. Bancorp (USB^A),USB^A
                    NYSE Equity,U.S. Bancorp (USB^H),USB^H
                    NYSE Equity,U.S. Bancorp (USB^M),USB^M
                    NYSE Equity,U.S. Bancorp (USB^O),USB^O
                    NYSE Equity,U.S. Bancorp (USB^P),USB^P
                    NYSE Equity,"U.S. Physical Therapy, Inc. (USPH)",USPH
                    NYSE Equity,"U.S. Silica Holdings, Inc. (SLCA)",SLCA
                    NYSE Equity,"U.S. Xpress Enterprises, Inc. (USX)",USX
                    NYSE Equity,"Uber Technologies, Inc. (UBER)",UBER
                    NYSE Equity,UBS AG (UBS),UBS
                    NYSE Equity,"UDR, Inc. (UDR)",UDR
                    NYSE Equity,UGI Corporation (UGI),UGI
                    NYSE Equity,Ultrapar Participacoes S.A. (UGP),UGP
                    NYSE Equity,"UMH Properties, Inc. (UMH)",UMH
                    NYSE Equity,"UMH Properties, Inc. (UMH^B)",UMH^B
                    NYSE Equity,"UMH Properties, Inc. (UMH^C)",UMH^C
                    NYSE Equity,"UMH Properties, Inc. (UMH^D)",UMH^D
                    NYSE Equity,"Under Armour, Inc. (UA)",UA
                    NYSE Equity,"Under Armour, Inc. (UAA)",UAA
                    NYSE Equity,"Unifi, Inc. (UFI)",UFI
                    NYSE Equity,Unifirst Corporation (UNF),UNF
                    NYSE Equity,Unilever NV (UN),UN
                    NYSE Equity,Unilever PLC (UL),UL
                    NYSE Equity,Union Pacific Corporation (UNP),UNP
                    NYSE Equity,Unisys Corporation (UIS),UIS
                    NYSE Equity,Unit Corporation (UNT),UNT
                    NYSE Equity,United Microelectronics Corporation (UMC),UMC
                    NYSE Equity,"United Natural Foods, Inc. (UNFI)",UNFI
                    NYSE Equity,"United Parcel Service, Inc. (UPS)",UPS
                    NYSE Equity,"United Rentals, Inc. (URI)",URI
                    NYSE Equity,United States Cellular Corporation (USM),USM
                    NYSE Equity,United States Cellular Corporation (UZA),UZA
                    NYSE Equity,United States Cellular Corporation (UZB),UZB
                    NYSE Equity,United States Cellular Corporation (UZC),UZC
                    NYSE Equity,United States Steel Corporation (X),X
                    NYSE Equity,United Technologies Corporation (UTX),UTX
                    NYSE Equity,UnitedHealth Group Incorporated (UNH),UNH
                    NYSE Equity,UNITIL Corporation (UTL),UTL
                    NYSE Equity,Univar Inc. (UNVR),UNVR
                    NYSE Equity,Universal Corporation (UVV),UVV
                    NYSE Equity,Universal Health Realty Income Trust (UHT),UHT
                    NYSE Equity,"Universal Health Services, Inc. (UHS)",UHS
                    NYSE Equity,UNIVERSAL INSURANCE HOLDINGS INC (UVE),UVE
                    NYSE Equity,Universal Technical Institute Inc (UTI),UTI
                    NYSE Equity,Unum Group (UNM),UNM
                    NYSE Equity,Unum Group (UNMA),UNMA
                    NYSE Equity,Urban Edge Properties (UE),UE
                    NYSE Equity,Urstadt Biddle Properties Inc. (UBA),UBA
                    NYSE Equity,Urstadt Biddle Properties Inc. (UBP),UBP
                    NYSE Equity,Urstadt Biddle Properties Inc. (UBP^G),UBP^G
                    NYSE Equity,Urstadt Biddle Properties Inc. (UBP^H),UBP^H
                    NYSE Equity,US Foods Holding Corp. (USFD),USFD
                    NYSE Equity,"USA Compression Partners, LP (USAC)",USAC
                    NYSE Equity,"USANA Health Sciences, Inc. (USNA)",USNA
                    NYSE Equity,USD Partners LP (USDP),USDP
                    NYSE Equity,"USLIFE Income Fund, Inc. (BIF)",BIF
                    NYSE Equity,V.F. Corporation (VFC),VFC
                    NYSE Equity,"VAALCO Energy, Inc.  (EGY)",EGY
                    NYSE Equity,"Vail Resorts, Inc. (MTN)",MTN
                    NYSE Equity,VALE S.A. (VALE),VALE
                    NYSE Equity,Valero Energy Corporation (VLO),VLO
                    NYSE Equity,"Valhi, Inc. (VHI)",VHI
                    NYSE Equity,"Valmont Industries, Inc. (VMI)",VMI
                    NYSE Equity,Valvoline Inc. (VVV),VVV
                    NYSE Equity,"Vapotherm, Inc. (VAPO)",VAPO
                    NYSE Equity,"Varian Medical Systems, Inc. (VAR)",VAR
                    NYSE Equity,Vector Group Ltd. (VGR),VGR
                    NYSE Equity,"Vectrus, Inc. (VEC)",VEC
                    NYSE Equity,Vedanta  Limited (VEDL),VEDL
                    NYSE Equity,Veeva Systems Inc. (VEEV),VEEV
                    NYSE Equity,Venator Materials PLC (VNTR),VNTR
                    NYSE Equity,"Ventas, Inc. (VTR)",VTR
                    NYSE Equity,"Veoneer, Inc. (VNE)",VNE
                    NYSE Equity,VEREIT Inc. (VER),VER
                    NYSE Equity,VEREIT Inc. (VER^F),VER^F
                    NYSE Equity,Veritiv Corporation (VRTV),VRTV
                    NYSE Equity,Verizon Communications Inc. (VZ),VZ
                    NYSE Equity,Vermilion Energy Inc. (VET),VET
                    NYSE Equity,Verso Corporation (VRS),VRS
                    NYSE Equity,"Versum Materials, Inc. (VSM)",VSM
                    NYSE Equity,Vertical Capital Income Fund (VCIF),VCIF
                    NYSE Equity,Viad Corp (VVI),VVI
                    NYSE Equity,VICI Properties Inc. (VICI),VICI
                    NYSE Equity,Vince Holding Corp. (VNCE),VNCE
                    NYSE Equity,Vipshop Holdings Limited (VIPS),VIPS
                    NYSE Equity,Virtus Global Dividend & Income Fund Inc. (ZTR),ZTR
                    NYSE Equity,Virtus Global Multi-Sector Income Fund (VGI),VGI
                    NYSE Equity,Virtus Total Return Fund Inc. (ZF),ZF
                    NYSE Equity,Visa Inc. (V),V
                    NYSE Equity,"Vishay Intertechnology, Inc. (VSH)",VSH
                    NYSE Equity,"Vishay Precision Group, Inc. (VPG)",VPG
                    NYSE Equity,Vista Outdoor Inc. (VSTO),VSTO
                    NYSE Equity,Vistra Energy Corp. (DYNC),DYNC
                    NYSE Equity,Vistra Energy Corp. (VST),VST
                    NYSE Equity,Vistra Energy Corp. (VST.WS.A),VST.WS.A
                    NYSE Equity,"Vitamin Shoppe, Inc (VSI)",VSI
                    NYSE Equity,"Vivint Solar, Inc. (VSLR)",VSLR
                    NYSE Equity,"Vmware, Inc. (VMW)",VMW
                    NYSE Equity,VOC Energy Trust (VOC),VOC
                    NYSE Equity,"Vocera Communications, Inc. (VCRA)",VCRA
                    NYSE Equity,Vonage Holdings Corp. (VG),VG
                    NYSE Equity,Vornado Realty Trust (VNO),VNO
                    NYSE Equity,Vornado Realty Trust (VNO^K),VNO^K
                    NYSE Equity,Vornado Realty Trust (VNO^L),VNO^L
                    NYSE Equity,Vornado Realty Trust (VNO^M),VNO^M
                    NYSE Equity,voxeljet AG (VJET),VJET
                    NYSE Equity,Voya Asia Pacific High Dividend Equity Income Fund (IAE),IAE
                    NYSE Equity,Voya Emerging Markets High Income Dividend Equity Fund (IHD),IHD
                    NYSE Equity,"Voya Financial, Inc. (VOYA)",VOYA
                    NYSE Equity,"Voya Financial, Inc. (VOYA^B)",VOYA^B
                    NYSE Equity,Voya Global Advantage and Premium Opportunity Fund (IGA),IGA
                    NYSE Equity,Voya Global Equity Dividend and Premium Opportunity Fund (IGD),IGD
                    NYSE Equity,"Voya Infrastructure, Industrials and Materials Fund (IDE)",IDE
                    NYSE Equity,Voya International High Dividend Equity Income Fund (IID),IID
                    NYSE Equity,Voya Natural Resources Equity Income Fund (IRR),IRR
                    NYSE Equity,Voya Prime Rate Trust (PPR),PPR
                    NYSE Equity,Vulcan Materials Company (VMC),VMC
                    NYSE Equity,"W&T Offshore, Inc. (WTI)",WTI
                    NYSE Equity,W.P. Carey Inc. (WPC),WPC
                    NYSE Equity,W.R. Berkley Corporation (WRB),WRB
                    NYSE Equity,W.R. Berkley Corporation (WRB^B),WRB^B
                    NYSE Equity,W.R. Berkley Corporation (WRB^C),WRB^C
                    NYSE Equity,W.R. Berkley Corporation (WRB^D),WRB^D
                    NYSE Equity,W.R. Berkley Corporation (WRB^E),WRB^E
                    NYSE Equity,W.R. Grace & Co. (GRA),GRA
                    NYSE Equity,"W.W. Grainger, Inc. (GWW)",GWW
                    NYSE Equity,Wabash National Corporation (WNC),WNC
                    NYSE Equity,Wabco Holdings Inc. (WBC),WBC
                    NYSE Equity,"Waddell & Reed Financial, Inc. (WDR)",WDR
                    NYSE Equity,"WageWorks, Inc. (WAGE)",WAGE
                    NYSE Equity,"Walker & Dunlop, Inc. (WD)",WD
                    NYSE Equity,Walmart Inc. (WMT),WMT
                    NYSE Equity,Walt Disney Company (The) (DIS),DIS
                    NYSE Equity,"Warrior Met Coal, Inc. (HCC)",HCC
                    NYSE Equity,Washington Prime Group Inc. (WPG),WPG
                    NYSE Equity,Washington Prime Group Inc. (WPG^H),WPG^H
                    NYSE Equity,Washington Prime Group Inc. (WPG^I),WPG^I
                    NYSE Equity,Washington Real Estate Investment Trust (WRE),WRE
                    NYSE Equity,"Waste Connections, Inc. (WCN)",WCN
                    NYSE Equity,"Waste Management, Inc. (WM)",WM
                    NYSE Equity,Waters Corporation (WAT),WAT
                    NYSE Equity,"Watsco, Inc. (WSO)",WSO
                    NYSE Equity,"Watsco, Inc. (WSO.B)",WSO.B
                    NYSE Equity,"Watts Water Technologies, Inc. (WTS)",WTS
                    NYSE Equity,Wayfair Inc. (W),W
                    NYSE Equity,Webster Financial Corporation (WBS),WBS
                    NYSE Equity,Webster Financial Corporation (WBS^F),WBS^F
                    NYSE Equity,"WEC Energy Group, Inc. (WEC)",WEC
                    NYSE Equity,Weidai Ltd. (WEI),WEI
                    NYSE Equity,Weingarten Realty Investors (WRI),WRI
                    NYSE Equity,"Weis Markets, Inc. (WMK)",WMK
                    NYSE Equity,"Welbilt, Inc. (WBT)",WBT
                    NYSE Equity,"WellCare Health Plans, Inc. (WCG)",WCG
                    NYSE Equity,Wells Fargo & Company (WFC),WFC
                    NYSE Equity,Wells Fargo & Company (WFC^L),WFC^L
                    NYSE Equity,Wells Fargo & Company (WFC^N),WFC^N
                    NYSE Equity,Wells Fargo & Company (WFC^O),WFC^O
                    NYSE Equity,Wells Fargo & Company (WFC^P),WFC^P
                    NYSE Equity,Wells Fargo & Company (WFC^Q),WFC^Q
                    NYSE Equity,Wells Fargo & Company (WFC^R),WFC^R
                    NYSE Equity,Wells Fargo & Company (WFC^T),WFC^T
                    NYSE Equity,Wells Fargo & Company (WFC^V),WFC^V
                    NYSE Equity,Wells Fargo & Company (WFC^W),WFC^W
                    NYSE Equity,Wells Fargo & Company (WFC^X),WFC^X
                    NYSE Equity,Wells Fargo & Company (WFC^Y),WFC^Y
                    NYSE Equity,Wells Fargo & Company (WFE^A),WFE^A
                    NYSE Equity,Wells Fargo Global Dividend Opportunity Fund (EOD),EOD
                    NYSE Equity,Welltower Inc. (WELL),WELL
                    NYSE Equity,"Wesco Aircraft Holdings, Inc. (WAIR)",WAIR
                    NYSE Equity,"WESCO International, Inc. (WCC)",WCC
                    NYSE Equity,"West Pharmaceutical Services, Inc. (WST)",WST
                    NYSE Equity,Western Alliance Bancorporation (WAL),WAL
                    NYSE Equity,Western Alliance Bancorporation (WALA),WALA
                    NYSE Equity,Western Asset Bond Fund (WEA),WEA
                    NYSE Equity,Western Asset Corporate Loan Fund Inc (TLI),TLI
                    NYSE Equity,Western Asset Emerging Markets Debt Fund Inc (EMD),EMD
                    NYSE Equity,Western Asset Global Corporate Defined Opportunity Fund Inc. (GDO),GDO
                    NYSE Equity,Western Asset Global High Income Fund Inc (EHI),EHI
                    NYSE Equity,Western Asset High Income Fund II Inc. (HIX),HIX
                    NYSE Equity,"Western Asset High Income Opportunity Fund, Inc. (HIO)",HIO
                    NYSE Equity,Western Asset High Yield Defined Opportunity Fund Inc. (HYI),HYI
                    NYSE Equity,Western Asset Intermediate Muni Fund Inc (SBI),SBI
                    NYSE Equity,Western Asset Investment Grade Defined Opportunity Trust Inc. (IGI),IGI
                    NYSE Equity,Western Asset Investment Grade Income Fund Inc. (PAI),PAI
                    NYSE Equity,"Western Asset Managed Municipals Fund, Inc. (MMU)",MMU
                    NYSE Equity,Western Asset Mortgage Capital Corporation (WMC),WMC
                    NYSE Equity,Western Asset Mortgage Defined Opportunity Fund Inc (DMO),DMO
                    NYSE Equity,Western Asset Municipal Defined Opportunity Trust Inc (MTT),MTT
                    NYSE Equity,"Western Asset Municipal High Income Fund, Inc. (MHF)",MHF
                    NYSE Equity,"Western Asset Municipal Partners Fund, Inc. (MNP)",MNP
                    NYSE Equity,Western Asset Variable Rate Strategic Fund Inc. (GFY),GFY
                    NYSE Equity,Western Asset/Claymore U.S Treasury Inflation Prot Secs Fd 2 (WIW),WIW
                    NYSE Equity,Western Asset/Claymore U.S. Treasury Inflation Prot Secs Fd (WIA),WIA
                    NYSE Equity,"Western Midstream Partners, LP (WES)",WES
                    NYSE Equity,Western Union Company (The) (WU),WU
                    NYSE Equity,Westinghouse Air Brake Technologies Corporation (WAB),WAB
                    NYSE Equity,Westlake Chemical Corporation (WLK),WLK
                    NYSE Equity,Westlake Chemical Partners LP (WLKP),WLKP
                    NYSE Equity,Westpac Banking Corporation (WBK),WBK
                    NYSE Equity,Westrock Company (WRK),WRK
                    NYSE Equity,Westwood Holdings Group Inc (WHG),WHG
                    NYSE Equity,WEX Inc. (WEX),WEX
                    NYSE Equity,Weyerhaeuser Company (WY),WY
                    NYSE Equity,Wheaton Precious Metals Corp. (WPM),WPM
                    NYSE Equity,Whirlpool Corporation (WHR),WHR
                    NYSE Equity,"White Mountains Insurance Group, Ltd. (WTM)",WTM
                    NYSE Equity,Whitestone REIT (WSR),WSR
                    NYSE Equity,Whiting Petroleum Corporation (WLL),WLL
                    NYSE Equity,"WideOpenWest, Inc. (WOW)",WOW
                    NYSE Equity,"Williams Companies, Inc. (The) (WMB)",WMB
                    NYSE Equity,"Williams-Sonoma, Inc. (WSM)",WSM
                    NYSE Equity,"Winnebago Industries, Inc. (WGO)",WGO
                    NYSE Equity,Wipro Limited (WIT),WIT
                    NYSE Equity,WNS (Holdings) Limited (WNS),WNS
                    NYSE Equity,"Wolverine World Wide, Inc. (WWW)",WWW
                    NYSE Equity,Woori Bank (WF),WF
                    NYSE Equity,Workiva Inc. (WK),WK
                    NYSE Equity,World Fuel Services Corporation (INT),INT
                    NYSE Equity,"World Wrestling Entertainment, Inc. (WWE)",WWE
                    NYSE Equity,"Worldpay, Inc. (WP)",WP
                    NYSE Equity,"Worthington Industries, Inc. (WOR)",WOR
                    NYSE Equity,WPP plc (WPP),WPP
                    NYSE Equity,"WPX Energy, Inc. (WPX)",WPX
                    NYSE Equity,"Wyndham Destinations, Inc. (WYND)",WYND
                    NYSE Equity,"Wyndham Hotels & Resorts, Inc. (WH)",WH
                    NYSE Equity,X Financial (XYF),XYF
                    NYSE Equity,XAI Octagon Floating Rate & Alternative Income Term Trust (XFLT),XFLT
                    NYSE Equity,"Xenia Hotels & Resorts, Inc. (XHR)",XHR
                    NYSE Equity,Xerox Corporation (XRX),XRX
                    NYSE Equity,Xinyuan Real Estate Co Ltd (XIN),XIN
                    NYSE Equity,"XPO Logistics, Inc. (XPO)",XPO
                    NYSE Equity,Xylem Inc. (XYL),XYL
                    NYSE Equity,Yamana Gold Inc. (AUY),AUY
                    NYSE Equity,Yelp Inc. (YELP),YELP
                    NYSE Equity,"YETI Holdings, Inc. (YETI)",YETI
                    NYSE Equity,"Yext, Inc. (YEXT)",YEXT
                    NYSE Equity,Yirendai Ltd. (YRD),YRD
                    NYSE Equity,YPF Sociedad Anonima (YPF),YPF
                    NYSE Equity,"Yum China Holdings, Inc. (YUMC)",YUMC
                    NYSE Equity,"Yum! Brands, Inc. (YUM)",YUM
                    NYSE Equity,"Zayo Group Holdings, Inc. (ZAYO)",ZAYO
                    NYSE Equity,"Zendesk, Inc. (ZEN)",ZEN
                    NYSE Equity,"Zimmer Biomet Holdings, Inc. (ZBH)",ZBH
                    NYSE Equity,Zions Bancorporation N.A. (ZB^A),ZB^A
                    NYSE Equity,Zions Bancorporation N.A. (ZB^G),ZB^G
                    NYSE Equity,Zions Bancorporation N.A. (ZB^H),ZB^H
                    NYSE Equity,Zions Bancorporation N.A. (ZBK),ZBK
                    NYSE Equity,Zoetis Inc. (ZTS),ZTS
                    NYSE Equity,ZTO Express (Cayman) Inc. (ZTO),ZTO
                    NYSE Equity,"Zuora, Inc. (ZUO)",ZUO
                    NYSE Equity,Zymeworks Inc. (ZYME),ZYME
                    S&P500,3M Company (MMM),MMM
                    S&P500,A.O. Smith Corp (AOS),AOS
                    S&P500,Abbott Laboratories (ABT),ABT
                    S&P500,AbbVie Inc. (ABBV),ABBV
                    S&P500,Accenture plc (ACN),ACN
                    S&P500,Activision Blizzard (ATVI),ATVI
                    S&P500,Acuity Brands Inc (AYI),AYI
                    S&P500,Adobe Systems Inc (ADBE),ADBE
                    S&P500,Advance Auto Parts (AAP),AAP
                    S&P500,Advanced Micro Devices Inc (AMD),AMD
                    S&P500,AES Corp (AES),AES
                    S&P500,Aetna Inc (AET),AET
                    S&P500,Affiliated Managers Group Inc (AMG),AMG
                    S&P500,AFLAC Inc (AFL),AFL
                    S&P500,Agilent Technologies Inc (A),A
                    S&P500,Air Products & Chemicals Inc (APD),APD
                    S&P500,Akamai Technologies Inc (AKAM),AKAM
                    S&P500,Alaska Air Group Inc (ALK),ALK
                    S&P500,Albemarle Corp (ALB),ALB
                    S&P500,Alexandria Real Estate Equities Inc (ARE),ARE
                    S&P500,Alexion Pharmaceuticals (ALXN),ALXN
                    S&P500,Align Technology (ALGN),ALGN
                    S&P500,Allegion (ALLE),ALLE
                    S&P500,"Allergan, Plc (AGN)",AGN
                    S&P500,Alliance Data Systems (ADS),ADS
                    S&P500,Alliant Energy Corp (LNT),LNT
                    S&P500,Allstate Corp (ALL),ALL
                    S&P500,Alphabet Inc Class A (GOOGL),GOOGL
                    S&P500,Alphabet Inc Class C (GOOG),GOOG
                    S&P500,Altria Group Inc (MO),MO
                    S&P500,Amazon.com Inc. (AMZN),AMZN
                    S&P500,Ameren Corp (AEE),AEE
                    S&P500,American Airlines Group (AAL),AAL
                    S&P500,American Electric Power (AEP),AEP
                    S&P500,American Express Co (AXP),AXP
                    S&P500,"American International Group, Inc. (AIG)",AIG
                    S&P500,American Tower Corp A (AMT),AMT
                    S&P500,American Water Works Company Inc (AWK),AWK
                    S&P500,Ameriprise Financial (AMP),AMP
                    S&P500,AmerisourceBergen Corp (ABC),ABC
                    S&P500,AMETEK Inc. (AME),AME
                    S&P500,Amgen Inc. (AMGN),AMGN
                    S&P500,Amphenol Corp (APH),APH
                    S&P500,Anadarko Petroleum Corp (APC),APC
                    S&P500,"Analog Devices, Inc. (ADI)",ADI
                    S&P500,Andeavor (ANDV),ANDV
                    S&P500,ANSYS (ANSS),ANSS
                    S&P500,Anthem Inc. (ANTM),ANTM
                    S&P500,Aon plc (AON),AON
                    S&P500,Apache Corporation (APA),APA
                    S&P500,Apartment Investment & Management (AIV),AIV
                    S&P500,Apple Inc. (AAPL),AAPL
                    S&P500,Applied Materials Inc. (AMAT),AMAT
                    S&P500,Aptiv Plc (APTV),APTV
                    S&P500,Archer-Daniels-Midland Co (ADM),ADM
                    S&P500,Arconic Inc. (ARNC),ARNC
                    S&P500,Arthur J. Gallagher & Co. (AJG),AJG
                    S&P500,Assurant Inc. (AIZ),AIZ
                    S&P500,AT&T Inc. (T),T
                    S&P500,Autodesk Inc. (ADSK),ADSK
                    S&P500,Automatic Data Processing (ADP),ADP
                    S&P500,AutoZone Inc (AZO),AZO
                    S&P500,"AvalonBay Communities, Inc. (AVB)",AVB
                    S&P500,Avery Dennison Corp (AVY),AVY
                    S&P500,"Baker Hughes, a GE Company (BHGE)",BHGE
                    S&P500,Ball Corp (BLL),BLL
                    S&P500,Bank of America Corp (BAC),BAC
                    S&P500,Baxter International Inc. (BAX),BAX
                    S&P500,BB&T Corporation (BBT),BBT
                    S&P500,Becton Dickinson (BDX),BDX
                    S&P500,Berkshire Hathaway (BRK.B),BRK.B
                    S&P500,Best Buy Co. Inc. (BBY),BBY
                    S&P500,Biogen Inc. (BIIB),BIIB
                    S&P500,BlackRock (BLK),BLK
                    S&P500,Block H&R (HRB),HRB
                    S&P500,Boeing Company (BA),BA
                    S&P500,Booking Holdings Inc (BKNG),BKNG
                    S&P500,BorgWarner (BWA),BWA
                    S&P500,Boston Properties (BXP),BXP
                    S&P500,Boston Scientific (BSX),BSX
                    S&P500,Brighthouse Financial Inc (BHF),BHF
                    S&P500,Bristol-Myers Squibb (BMY),BMY
                    S&P500,Broadcom (AVGO),AVGO
                    S&P500,Brown-Forman Corp. (BF.B),BF.B
                    S&P500,C. H. Robinson Worldwide (CHRW),CHRW
                    S&P500,"CA, Inc. (CA)",CA
                    S&P500,Cabot Oil & Gas (COG),COG
                    S&P500,Cadence Design Systems (CDNS),CDNS
                    S&P500,Campbell Soup (CPB),CPB
                    S&P500,Capital One Financial (COF),COF
                    S&P500,Cardinal Health Inc. (CAH),CAH
                    S&P500,Carmax Inc (KMX),KMX
                    S&P500,Carnival Corp. (CCL),CCL
                    S&P500,Caterpillar Inc. (CAT),CAT
                    S&P500,Cboe Global Markets (CBOE),CBOE
                    S&P500,CBRE Group (CBRE),CBRE
                    S&P500,CBS Corp. (CBS),CBS
                    S&P500,Celgene Corp. (CELG),CELG
                    S&P500,Centene Corporation (CNC),CNC
                    S&P500,CenterPoint Energy (CNP),CNP
                    S&P500,CenturyLink Inc (CTL),CTL
                    S&P500,Cerner (CERN),CERN
                    S&P500,CF Industries Holdings Inc (CF),CF
                    S&P500,Charles Schwab Corporation (SCHW),SCHW
                    S&P500,Charter Communications (CHTR),CHTR
                    S&P500,Chevron Corp. (CVX),CVX
                    S&P500,Chipotle Mexican Grill (CMG),CMG
                    S&P500,Chubb Limited (CB),CB
                    S&P500,Church & Dwight (CHD),CHD
                    S&P500,CIGNA Corp. (CI),CI
                    S&P500,Cimarex Energy (XEC),XEC
                    S&P500,Cincinnati Financial (CINF),CINF
                    S&P500,Cintas Corporation (CTAS),CTAS
                    S&P500,Cisco Systems (CSCO),CSCO
                    S&P500,Citigroup Inc. (C),C
                    S&P500,Citizens Financial Group (CFG),CFG
                    S&P500,Citrix Systems (CTXS),CTXS
                    S&P500,CME Group Inc. (CME),CME
                    S&P500,CMS Energy (CMS),CMS
                    S&P500,Coca-Cola Company (The) (KO),KO
                    S&P500,Cognizant Technology Solutions (CTSH),CTSH
                    S&P500,Colgate-Palmolive (CL),CL
                    S&P500,Comcast Corp. (CMCSA),CMCSA
                    S&P500,Comerica Inc. (CMA),CMA
                    S&P500,Conagra Brands (CAG),CAG
                    S&P500,Concho Resources (CXO),CXO
                    S&P500,ConocoPhillips (COP),COP
                    S&P500,Consolidated Edison (ED),ED
                    S&P500,Constellation Brands (STZ),STZ
                    S&P500,Corning Inc. (GLW),GLW
                    S&P500,Costco Wholesale Corp. (COST),COST
                    S&P500,"Coty, Inc (COTY)",COTY
                    S&P500,Crown Castle International Corp. (CCI),CCI
                    S&P500,CSRA Inc. (CSRA),CSRA
                    S&P500,CSX Corp. (CSX),CSX
                    S&P500,Cummins Inc. (CMI),CMI
                    S&P500,CVS Health (CVS),CVS
                    S&P500,D. R. Horton (DHI),DHI
                    S&P500,Danaher Corp. (DHR),DHR
                    S&P500,Darden Restaurants (DRI),DRI
                    S&P500,DaVita Inc. (DVA),DVA
                    S&P500,Deere & Co. (DE),DE
                    S&P500,Delta Air Lines Inc. (DAL),DAL
                    S&P500,Dentsply Sirona (XRAY),XRAY
                    S&P500,Devon Energy Corp. (DVN),DVN
                    S&P500,Digital Realty Trust Inc (DLR),DLR
                    S&P500,Discover Financial Services (DFS),DFS
                    S&P500,Discovery Inc. Class A (DISCA),DISCA
                    S&P500,Discovery Inc. Class C (DISCK),DISCK
                    S&P500,Dish Network (DISH),DISH
                    S&P500,Dollar General (DG),DG
                    S&P500,Dollar Tree (DLTR),DLTR
                    S&P500,Dominion Energy (D),D
                    S&P500,Dover Corp. (DOV),DOV
                    S&P500,DowDuPont (DWDP),DWDP
                    S&P500,Dr Pepper Snapple Group (DPS),DPS
                    S&P500,DTE Energy Co. (DTE),DTE
                    S&P500,Duke Energy (DUK),DUK
                    S&P500,Duke Realty Corp (DRE),DRE
                    S&P500,DXC Technology (DXC),DXC
                    S&P500,E*Trade (ETFC),ETFC
                    S&P500,Eastman Chemical (EMN),EMN
                    S&P500,Eaton Corporation (ETN),ETN
                    S&P500,eBay Inc. (EBAY),EBAY
                    S&P500,Ecolab Inc. (ECL),ECL
                    S&P500,Edison Int'l (EIX),EIX
                    S&P500,Edwards Lifesciences (EW),EW
                    S&P500,Electronic Arts (EA),EA
                    S&P500,Emerson Electric Company (EMR),EMR
                    S&P500,Entergy Corp. (ETR),ETR
                    S&P500,Envision Healthcare (EVHC),EVHC
                    S&P500,EOG Resources (EOG),EOG
                    S&P500,EQT Corporation (EQT),EQT
                    S&P500,Equifax Inc. (EFX),EFX
                    S&P500,Equinix (EQIX),EQIX
                    S&P500,Equity Residential (EQR),EQR
                    S&P500,"Essex Property Trust, Inc. (ESS)",ESS
                    S&P500,Estee Lauder Cos. (EL),EL
                    S&P500,Everest Re Group Ltd. (RE),RE
                    S&P500,Eversource Energy (ES),ES
                    S&P500,Exelon Corp. (EXC),EXC
                    S&P500,Expedia Inc. (EXPE),EXPE
                    S&P500,Expeditors International (EXPD),EXPD
                    S&P500,Express Scripts (ESRX),ESRX
                    S&P500,Extra Space Storage (EXR),EXR
                    S&P500,Exxon Mobil Corp. (XOM),XOM
                    S&P500,F5 Networks (FFIV),FFIV
                    S&P500,"Facebook, Inc. (FB)",FB
                    S&P500,Fastenal Co (FAST),FAST
                    S&P500,Federal Realty Investment Trust (FRT),FRT
                    S&P500,FedEx Corporation (FDX),FDX
                    S&P500,Fidelity National Information Services (FIS),FIS
                    S&P500,Fifth Third Bancorp (FITB),FITB
                    S&P500,FirstEnergy Corp (FE),FE
                    S&P500,Fiserv Inc (FISV),FISV
                    S&P500,FLIR Systems (FLIR),FLIR
                    S&P500,Flowserve Corporation (FLS),FLS
                    S&P500,Fluor Corp. (FLR),FLR
                    S&P500,FMC Corporation (FMC),FMC
                    S&P500,Foot Locker Inc (FL),FL
                    S&P500,Ford Motor (F),F
                    S&P500,Fortive Corp (FTV),FTV
                    S&P500,Fortune Brands Home & Security (FBHS),FBHS
                    S&P500,Franklin Resources (BEN),BEN
                    S&P500,Freeport-McMoRan Inc. (FCX),FCX
                    S&P500,Gap Inc. (GPS),GPS
                    S&P500,Garmin Ltd. (GRMN),GRMN
                    S&P500,Gartner Inc (IT),IT
                    S&P500,General Dynamics (GD),GD
                    S&P500,General Electric (GE),GE
                    S&P500,General Growth Properties Inc. (GGP),GGP
                    S&P500,General Mills (GIS),GIS
                    S&P500,General Motors (GM),GM
                    S&P500,Genuine Parts (GPC),GPC
                    S&P500,Gilead Sciences (GILD),GILD
                    S&P500,Global Payments Inc. (GPN),GPN
                    S&P500,Goldman Sachs Group (GS),GS
                    S&P500,Goodyear Tire & Rubber (GT),GT
                    S&P500,Grainger (W.W.) Inc. (GWW),GWW
                    S&P500,Halliburton Co. (HAL),HAL
                    S&P500,Hanesbrands Inc (HBI),HBI
                    S&P500,Harley-Davidson (HOG),HOG
                    S&P500,Harris Corporation (HRS),HRS
                    S&P500,Hartford Financial Svc.Gp. (HIG),HIG
                    S&P500,Hasbro Inc. (HAS),HAS
                    S&P500,HCA Holdings (HCA),HCA
                    S&P500,HCP Inc. (HCP),HCP
                    S&P500,Helmerich & Payne (HP),HP
                    S&P500,Henry Schein (HSIC),HSIC
                    S&P500,Hess Corporation (HES),HES
                    S&P500,Hewlett Packard Enterprise (HPE),HPE
                    S&P500,Hilton Worldwide Holdings Inc (HLT),HLT
                    S&P500,Hologic (HOLX),HOLX
                    S&P500,Home Depot (HD),HD
                    S&P500,Honeywell Int'l Inc. (HON),HON
                    S&P500,Hormel Foods Corp. (HRL),HRL
                    S&P500,Host Hotels & Resorts (HST),HST
                    S&P500,HP Inc. (HPQ),HPQ
                    S&P500,Humana Inc. (HUM),HUM
                    S&P500,Huntington Bancshares (HBAN),HBAN
                    S&P500,Huntington Ingalls Industries (HII),HII
                    S&P500,IDEXX Laboratories (IDXX),IDXX
                    S&P500,IHS Markit Ltd. (INFO),INFO
                    S&P500,Illinois Tool Works (ITW),ITW
                    S&P500,Illumina Inc (ILMN),ILMN
                    S&P500,Incyte (INCY),INCY
                    S&P500,Ingersoll-Rand PLC (IR),IR
                    S&P500,Intel Corp. (INTC),INTC
                    S&P500,Intercontinental Exchange (ICE),ICE
                    S&P500,International Business Machines (IBM),IBM
                    S&P500,International Paper (IP),IP
                    S&P500,Interpublic Group (IPG),IPG
                    S&P500,Intl Flavors & Fragrances (IFF),IFF
                    S&P500,Intuit Inc. (INTU),INTU
                    S&P500,Intuitive Surgical Inc. (ISRG),ISRG
                    S&P500,Invesco Ltd. (IVZ),IVZ
                    S&P500,IPG Photonics Corp. (IPGP),IPGP
                    S&P500,IQVIA Holdings Inc. (IQV),IQV
                    S&P500,Iron Mountain Incorporated (IRM),IRM
                    S&P500,J. B. Hunt Transport Services (JBHT),JBHT
                    S&P500,Jacobs Engineering Group (JEC),JEC
                    S&P500,JM Smucker (SJM),SJM
                    S&P500,Johnson & Johnson (JNJ),JNJ
                    S&P500,Johnson Controls International (JCI),JCI
                    S&P500,JPMorgan Chase & Co. (JPM),JPM
                    S&P500,Juniper Networks (JNPR),JNPR
                    S&P500,Kansas City Southern (KSU),KSU
                    S&P500,Kellogg Co. (K),K
                    S&P500,KeyCorp (KEY),KEY
                    S&P500,Kimberly-Clark (KMB),KMB
                    S&P500,Kimco Realty (KIM),KIM
                    S&P500,Kinder Morgan (KMI),KMI
                    S&P500,KLA-Tencor Corp. (KLAC),KLAC
                    S&P500,Kohl's Corp. (KSS),KSS
                    S&P500,Kraft Heinz Co (KHC),KHC
                    S&P500,Kroger Co. (KR),KR
                    S&P500,L Brands Inc. (LB),LB
                    S&P500,L-3 Communications Holdings (LLL),LLL
                    S&P500,Laboratory Corp. of America Holding (LH),LH
                    S&P500,Lam Research (LRCX),LRCX
                    S&P500,Leggett & Platt (LEG),LEG
                    S&P500,Lennar Corp. (LEN),LEN
                    S&P500,Leucadia National Corp. (LUK),LUK
                    S&P500,Lilly (Eli) & Co. (LLY),LLY
                    S&P500,Lincoln National (LNC),LNC
                    S&P500,LKQ Corporation (LKQ),LKQ
                    S&P500,Lockheed Martin Corp. (LMT),LMT
                    S&P500,Loews Corp. (L),L
                    S&P500,Lowe's Cos. (LOW),LOW
                    S&P500,LyondellBasell (LYB),LYB
                    S&P500,M&T Bank Corp. (MTB),MTB
                    S&P500,Macerich (MAC),MAC
                    S&P500,Macy's Inc. (M),M
                    S&P500,Marathon Oil Corp. (MRO),MRO
                    S&P500,Marathon Petroleum (MPC),MPC
                    S&P500,Marriott Int'l. (MAR),MAR
                    S&P500,Marsh & McLennan (MMC),MMC
                    S&P500,Martin Marietta Materials (MLM),MLM
                    S&P500,Masco Corp. (MAS),MAS
                    S&P500,Mastercard Inc. (MA),MA
                    S&P500,Mattel Inc. (MAT),MAT
                    S&P500,McCormick & Co. (MKC),MKC
                    S&P500,McDonald's Corp. (MCD),MCD
                    S&P500,McKesson Corp. (MCK),MCK
                    S&P500,Medtronic plc (MDT),MDT
                    S&P500,Merck & Co. (MRK),MRK
                    S&P500,MetLife Inc. (MET),MET
                    S&P500,Mettler Toledo (MTD),MTD
                    S&P500,MGM Resorts International (MGM),MGM
                    S&P500,Michael Kors Holdings (KORS),KORS
                    S&P500,Microchip Technology (MCHP),MCHP
                    S&P500,Micron Technology (MU),MU
                    S&P500,Microsoft Corp. (MSFT),MSFT
                    S&P500,Mid-America Apartments (MAA),MAA
                    S&P500,Mohawk Industries (MHK),MHK
                    S&P500,Molson Coors Brewing Company (TAP),TAP
                    S&P500,Mondelez International (MDLZ),MDLZ
                    S&P500,Monsanto Co. (MON),MON
                    S&P500,Monster Beverage (MNST),MNST
                    S&P500,Moody's Corp (MCO),MCO
                    S&P500,Morgan Stanley (MS),MS
                    S&P500,Motorola Solutions Inc. (MSI),MSI
                    S&P500,Mylan N.V. (MYL),MYL
                    S&P500,"Nasdaq, Inc. (NDAQ)",NDAQ
                    S&P500,National Oilwell Varco Inc. (NOV),NOV
                    S&P500,Navient (NAVI),NAVI
                    S&P500,Nektar Therapeutics (NKTR),NKTR
                    S&P500,NetApp (NTAP),NTAP
                    S&P500,Netflix Inc. (NFLX),NFLX
                    S&P500,Newell Brands (NWL),NWL
                    S&P500,Newfield Exploration Co (NFX),NFX
                    S&P500,Newmont Mining Corporation (NEM),NEM
                    S&P500,News Corp. Class A (NWSA),NWSA
                    S&P500,News Corp. Class B (NWS),NWS
                    S&P500,NextEra Energy (NEE),NEE
                    S&P500,Nielsen Holdings (NLSN),NLSN
                    S&P500,Nike (NKE),NKE
                    S&P500,NiSource Inc. (NI),NI
                    S&P500,Noble Energy Inc (NBL),NBL
                    S&P500,Nordstrom (JWN),JWN
                    S&P500,Norfolk Southern Corp. (NSC),NSC
                    S&P500,Northern Trust Corp. (NTRS),NTRS
                    S&P500,Northrop Grumman Corp. (NOC),NOC
                    S&P500,Norwegian Cruise Line (NCLH),NCLH
                    S&P500,NRG Energy (NRG),NRG
                    S&P500,Nucor Corp. (NUE),NUE
                    S&P500,Nvidia Corporation (NVDA),NVDA
                    S&P500,O'Reilly Automotive (ORLY),ORLY
                    S&P500,Occidental Petroleum (OXY),OXY
                    S&P500,Omnicom Group (OMC),OMC
                    S&P500,ONEOK (OKE),OKE
                    S&P500,Oracle Corp. (ORCL),ORCL
                    S&P500,PACCAR Inc. (PCAR),PCAR
                    S&P500,Packaging Corporation of America (PKG),PKG
                    S&P500,Parker-Hannifin (PH),PH
                    S&P500,Paychex Inc. (PAYX),PAYX
                    S&P500,PayPal (PYPL),PYPL
                    S&P500,Pentair Ltd. (PNR),PNR
                    S&P500,People's United Financial (PBCT),PBCT
                    S&P500,PepsiCo Inc. (PEP),PEP
                    S&P500,PerkinElmer (PKI),PKI
                    S&P500,Perrigo (PRGO),PRGO
                    S&P500,Pfizer Inc. (PFE),PFE
                    S&P500,PG&E Corp. (PCG),PCG
                    S&P500,Philip Morris International (PM),PM
                    S&P500,Phillips 66 (PSX),PSX
                    S&P500,Pinnacle West Capital (PNW),PNW
                    S&P500,Pioneer Natural Resources (PXD),PXD
                    S&P500,PNC Financial Services (PNC),PNC
                    S&P500,Polo Ralph Lauren Corp. (RL),RL
                    S&P500,PPG Industries (PPG),PPG
                    S&P500,PPL Corp. (PPL),PPL
                    S&P500,Praxair Inc. (PX),PX
                    S&P500,Principal Financial Group (PFG),PFG
                    S&P500,Procter & Gamble (PG),PG
                    S&P500,Progressive Corp. (PGR),PGR
                    S&P500,Prologis (PLD),PLD
                    S&P500,Prudential Financial (PRU),PRU
                    S&P500,Public Serv. Enterprise Inc. (PEG),PEG
                    S&P500,Public Storage (PSA),PSA
                    S&P500,Pulte Homes Inc. (PHM),PHM
                    S&P500,PVH Corp. (PVH),PVH
                    S&P500,Qorvo (QRVO),QRVO
                    S&P500,QUALCOMM Inc. (QCOM),QCOM
                    S&P500,Quanta Services Inc. (PWR),PWR
                    S&P500,Quest Diagnostics (DGX),DGX
                    S&P500,Range Resources Corp. (RRC),RRC
                    S&P500,Raymond James Financial Inc. (RJF),RJF
                    S&P500,Raytheon Co. (RTN),RTN
                    S&P500,Realty Income Corporation (O),O
                    S&P500,Red Hat Inc. (RHT),RHT
                    S&P500,Regency Centers Corporation (REG),REG
                    S&P500,Regeneron (REGN),REGN
                    S&P500,Regions Financial Corp. (RF),RF
                    S&P500,Republic Services Inc (RSG),RSG
                    S&P500,ResMed (RMD),RMD
                    S&P500,Robert Half International (RHI),RHI
                    S&P500,Rockwell Automation Inc. (ROK),ROK
                    S&P500,Rockwell Collins (COL),COL
                    S&P500,Roper Technologies (ROP),ROP
                    S&P500,Ross Stores (ROST),ROST
                    S&P500,Royal Caribbean Cruises Ltd (RCL),RCL
                    S&P500,"S&P Global, Inc. (SPGI)",SPGI
                    S&P500,Salesforce.com (CRM),CRM
                    S&P500,SBA Communications (SBAC),SBAC
                    S&P500,SCANA Corp (SCG),SCG
                    S&P500,Schlumberger Ltd. (SLB),SLB
                    S&P500,Seagate Technology (STX),STX
                    S&P500,Sealed Air (SEE),SEE
                    S&P500,Sempra Energy (SRE),SRE
                    S&P500,Sherwin-Williams (SHW),SHW
                    S&P500,Simon Property Group Inc (SPG),SPG
                    S&P500,Skyworks Solutions (SWKS),SWKS
                    S&P500,SL Green Realty (SLG),SLG
                    S&P500,Snap-On Inc. (SNA),SNA
                    S&P500,Southern Co. (SO),SO
                    S&P500,Southwest Airlines (LUV),LUV
                    S&P500,Stanley Black & Decker (SWK),SWK
                    S&P500,Starbucks Corp. (SBUX),SBUX
                    S&P500,State Street Corp. (STT),STT
                    S&P500,Stericycle Inc (SRCL),SRCL
                    S&P500,Stryker Corp. (SYK),SYK
                    S&P500,SunTrust Banks (STI),STI
                    S&P500,SVB Financial (SIVB),SIVB
                    S&P500,Symantec Corp. (SYMC),SYMC
                    S&P500,Synchrony Financial (SYF),SYF
                    S&P500,Synopsys Inc. (SNPS),SNPS
                    S&P500,Sysco Corp. (SYY),SYY
                    S&P500,T. Rowe Price Group (TROW),TROW
                    S&P500,Take-Two Interactive (TTWO),TTWO
                    S&P500,"Tapestry, Inc. (TPR)",TPR
                    S&P500,Target Corp. (TGT),TGT
                    S&P500,TE Connectivity Ltd. (TEL),TEL
                    S&P500,TechnipFMC (FTI),FTI
                    S&P500,Texas Instruments (TXN),TXN
                    S&P500,Textron Inc. (TXT),TXT
                    S&P500,The Bank of New York Mellon Corp. (BK),BK
                    S&P500,The Clorox Company (CLX),CLX
                    S&P500,The Cooper Companies (COO),COO
                    S&P500,The Hershey Company (HSY),HSY
                    S&P500,The Mosaic Company (MOS),MOS
                    S&P500,The Travelers Companies Inc. (TRV),TRV
                    S&P500,The Walt Disney Company (DIS),DIS
                    S&P500,Thermo Fisher Scientific (TMO),TMO
                    S&P500,Tiffany & Co. (TIF),TIF
                    S&P500,Time Warner Inc. (TWX),TWX
                    S&P500,TJX Companies Inc. (TJX),TJX
                    S&P500,Torchmark Corp. (TMK),TMK
                    S&P500,Total System Services (TSS),TSS
                    S&P500,Tractor Supply Company (TSCO),TSCO
                    S&P500,TransDigm Group (TDG),TDG
                    S&P500,TripAdvisor (TRIP),TRIP
                    S&P500,Twenty-First Century Fox Class A (FOXA),FOXA
                    S&P500,Twenty-First Century Fox Class B (FOX),FOX
                    S&P500,Tyson Foods (TSN),TSN
                    S&P500,U.S. Bancorp (USB),USB
                    S&P500,UDR Inc (UDR),UDR
                    S&P500,Ulta Beauty (ULTA),ULTA
                    S&P500,Under Armour Class A (UAA),UAA
                    S&P500,Under Armour Class C (UA),UA
                    S&P500,Union Pacific (UNP),UNP
                    S&P500,United Continental Holdings (UAL),UAL
                    S&P500,United Health Group Inc. (UNH),UNH
                    S&P500,United Parcel Service (UPS),UPS
                    S&P500,"United Rentals, Inc. (URI)",URI
                    S&P500,United Technologies (UTX),UTX
                    S&P500,"Universal Health Services, Inc. (UHS)",UHS
                    S&P500,Unum Group (UNM),UNM
                    S&P500,V.F. Corp. (VFC),VFC
                    S&P500,Valero Energy (VLO),VLO
                    S&P500,Varian Medical Systems (VAR),VAR
                    S&P500,Ventas Inc (VTR),VTR
                    S&P500,Verisign Inc. (VRSN),VRSN
                    S&P500,Verisk Analytics (VRSK),VRSK
                    S&P500,Verizon Communications (VZ),VZ
                    S&P500,Vertex Pharmaceuticals Inc (VRTX),VRTX
                    S&P500,Viacom Inc. (VIAB),VIAB
                    S&P500,Visa Inc. (V),V
                    S&P500,Vornado Realty Trust (VNO),VNO
                    S&P500,Vulcan Materials (VMC),VMC
                    S&P500,Wal-Mart Stores (WMT),WMT
                    S&P500,Walgreens Boots Alliance (WBA),WBA
                    S&P500,Waste Management Inc. (WM),WM
                    S&P500,Waters Corporation (WAT),WAT
                    S&P500,Wec Energy Group Inc (WEC),WEC
                    S&P500,Wells Fargo (WFC),WFC
                    S&P500,Welltower Inc. (WELL),WELL
                    S&P500,Western Digital (WDC),WDC
                    S&P500,Western Union Co (WU),WU
                    S&P500,WestRock Company (WRK),WRK
                    S&P500,Weyerhaeuser Corp. (WY),WY
                    S&P500,Whirlpool Corp. (WHR),WHR
                    S&P500,Williams Cos. (WMB),WMB
                    S&P500,Willis Towers Watson (WLTW),WLTW
                    S&P500,Wyndham Worldwide (WYN),WYN
                    S&P500,Wynn Resorts Ltd (WYNN),WYNN
                    S&P500,Xcel Energy Inc (XEL),XEL
                    S&P500,Xerox Corp. (XRX),XRX
                    S&P500,Xilinx Inc (XLNX),XLNX
                    S&P500,XL Capital (XL),XL
                    S&P500,Xylem Inc. (XYL),XYL
                    S&P500,Yum! Brands Inc (YUM),YUM
                    S&P500,Zimmer Biomet Holdings (ZBH),ZBH
                    S&P500,Zions Bancorp (ZION),ZION
                    S&P500,Zoetis (ZTS),ZTS"""
ticker_dict = defaultdict(list)
for line in ticker_string.splitlines():
    line_list = line.split(',')
    ticker_dict['type'].append(line_list[0].strip())
    ticker_dict['name'].append(line_list[1].strip())
    ticker_dict['code'].append(line_list[2].strip())
df_0 = pd.DataFrame(ticker_dict)

months = ["January","February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

session = FuturesSession()

FRED_cache_dir = 'FRED_cache'
# if not os.path.exists(FRED_cache_dir):
#     os.mkdir(FRED_cache_dir)
    
ticker_cache_dir = 'ticker_cache'
# if not os.path.exists(ticker_cache_dir):
#     os.mkdir(ticker_cache_dir)

fit_cache_dir = 'fit_cache'
# if not os.path.exists(fit_cache_dir):
#     os.mkdir(fit_cache_dir)

ticker = 'GOOG'
commodity_type = 'NYSE Equity'

function_groups = talib.get_function_groups()
functions = talib.get_functions()
pattern_list = [function for function in function_groups['Pattern Recognition'] ]
pattern_names = ['2 CROWS', '3 BLACK CROWS', '3 INSIDE', '3 LINE STRIKE', '3 OUTSIDE', '3 STARS IN THE SOUTH',
                    '3 WHITE SOLDIERS', 'ABANDONED BABY', 'ADVANCE BLOCK', 'BELTHOLD', 'BREAKAWAY', 'CLOSING MARUBOZU',
                    'CONCEAL BABY SWALL', 'COUNTERATTACK', 'DARK CLOUD COVER', 'DOJI', 'DOJI STAR', 'DRAGONFLY DOJI', 'ENGULFING',
                    'EVENING DOJISTAR', 'EVENING STAR', 'GAP-SIDE SIDE-WHITE', 'GRAVESTONE DOJI', 'HAMMER', 'HANGINGMAN',
                    'HARAMI', 'HARAMI CROSS', 'HIGH WAVE', 'HIKKAKE', 'HIKKAKE MOD', 'HOMING PIGEON', 'IDENTICAL 3 CROWS',
                    'IN-NECK', 'INVERTED HAMMER', 'KICKING', 'KICKING BY LENGTH', 'LADDER BOTTOM', 'LONG-LEGGED DOJI',
                    'LONG LINE', 'MARUBOZU', 'MATCHING LOW', 'MATHOLD', 'MORNING DOJI STAR', 'MORNING STAR', 'ON NECK',
                    'PIERCING', 'RICKSHAW MAN', 'RISE-FALL 3-METHODS', 'SEPARATING LINES', 'SHOOTING STAR', 'SHORT LINE',
                    'SPINNING TOP', 'STALLED PATTERN', 'STICK SANDWICH', 'TAKURI', 'TASUKI GAP', 'THRUSTING', 'TRI-STAR',
                    'UNIQUE 3 RIVER', 'UP-SIDE GAP 2 CROWS', 'X-SIDE GAP 3 METHODS']
pattern_dict = {k:v for k,v in zip(pattern_list, pattern_names)}

# Set ML parameters
dict_classifiers = {"Logistic Regression": LogisticRegression(C=10.0, penalty='l1'),
                    "Nearest Neighbors": KNeighborsClassifier(metric='euclidean', n_neighbors=3, weights='uniform'),
                    "Decision Tree": tree.DecisionTreeClassifier(max_depth=19, min_samples_leaf=10),
                    "AdaBoost": AdaBoostClassifier(learning_rate=0.01, n_estimators=1000),
                    "Naive Bayes": GaussianNB(),
                    "QDA": QuadraticDiscriminantAnalysis(),
                    "Linear SVM": SVC(C=1, gamma=0.1),
                    "Gradient Boosting Classifier": GradientBoostingClassifier(n_estimators=1000, learning_rate=0.001, 
                                                                               max_depth=6, criterion='friedman_mse'),
                    "Gaussian Process": GaussianProcessClassifier(),
                    "Random Forest": RandomForestClassifier(n_estimators=362, max_features='auto', min_samples_split=3, max_depth=30,
                                                            min_samples_leaf=2, bootstrap=True),
                    "Neural Net":  MLPClassifier(alpha = 0.01, solver='lbfgs', max_iter=610, hidden_layer_sizes=5, random_state=0),
                    }
Voters = dict_classifiers.values()
dict_classifiers["Voter"] = VotingClassifier([Voters], voting='hard', n_jobs=-1)

GBC_params = {'n_estimators': [100, 500, 1000],
              'learning_rate': [0.1, 0.01, 0.001],
              'criterion': ['friedman_mse', 'mse', 'mae']}

LR_params = {"C":np.logspace(-3,3,7), "penalty":["l1","l2"]}

kNN_params = {'n_neighbors': [3, 5, 11, 19],
             'weights': ['uniform', 'distance'],
             'metric': ['euclidean', 'manhattan']}

SVM_params = {'C': [0.001, 0.01, 0.1, 1, 10],
              'gamma' : [0.001, 0.01, 0.1, 1]}

DT_params = {'max_depth': np.arange(1, 21, 2),
             'min_samples_leaf': [1, 2, 5, 10, 20, 50]} #[]

RF_params = {'n_estimators': [int(x) for x in np.linspace(start = 200, stop = 2000, num = 200)],
             'max_features': ['auto', 'sqrt'],
             'max_depth': [int(x) for x in np.linspace(10, 110, num = 11)]+[None],
             'min_samples_split': [2, 5, 10],
             'min_samples_leaf': [1, 2, 4],
             'bootstrap': [True, False]}

NN_params = {'solver': ['lbfgs'], 'max_iter': [500, 1000, 1500], 
             'alpha': 10.0 ** -np.arange(1, 7), 'hidden_layer_sizes':np.arange(5, 12), 
             'random_state':[0,1,2,3,4,5,6,7,8,9]}

AB_params = {'n_estimators':[500,1000,2000],'learning_rate':[.001,0.01,.1]}

dict_classifier_params = {"Logistic Regression": LR_params,
                          "Nearest Neighbors": kNN_params,
                          "Decision Tree": DT_params,
                          "AdaBoost": AB_params,
                          "Naive Bayes": {},
                          "QDA": {},
                          "Linear SVM": SVM_params,
                          "Gradient Boosting Classifier": GBC_params,
                          "Gaussian Process": {},
                          "Random Forest": RF_params,
                          "Neural Net": NN_params}

dense = ['Naive Bayes', 'QDA', 'Gaussian Process', 'Voter']

searchable = ['Neural Net']

# helper functions
def float_or_NaN(s):
    try: 
        r = float(s)
    except:
        r = float('NaN')
    return r

def get_bounds(col):
    mn = df_ticker[col].min()
    mx = df_ticker[col].max()
    rn = mx - mn
    return mn - 0.05*rn , mx + 0.05*rn

def SMA(n, s):
        return [s[0]]*n+[np.mean(s[i-n:i]) for i in range(n,len(s))]

def EMA(n, s):
    k = 2/(n+1)
    ema = np.zeros(len(s))
    ema[0] = s[0]
    for i in range(1, len(s)-1):
        ema[i] = k*s[i] + (1-k)*ema[i-1]
    return ema

def get_FRED_data(FRED_cache_dir, use_cache=False):
    fr = Fred(api_key=FRED_API_Key, response_type='df')
    try:
        if use_cache:
            df_FRED = pd.read_csv(f'.\{FRED_cache_dir}\FRED.csv', index_col='date', parse_dates=True)
            print('FRED data retrieved from cache')
            FRED_series = pd.read_csv(f'.\{FRED_cache_dir}\FRED_series.csv')[['Series ID', 'Series Title']]
            update_time = pd.Timestamp.strftime(pd.date_range(df_FRED.index[-1], periods=2, freq='D')[1], '%Y-%m-%d')
            df_FRED_update = dl_FRED(FRED_series, update_time)
            df_FRED = df_FRED.append(df_FRED_update, verify_integrity=True, sort=False)
        if not use_cache:
            print('Ignoring cache, downloading from API.')
            FRED_series = get_FRED_series()
            df_FRED = dl_FRED(FRED_series, None)
        FRED_series.to_csv(f'.\{FRED_cache_dir}\FRED_series.csv', index=False)
        df_FRED.to_csv(f'.\{FRED_cache_dir}\FRED.csv')
        print('FRED data and series saved to cache')
        return df_FRED
    except:
        raise Exception('Failed FRED Acquisition.')
        print('Failed FRED Acquisition.')
        return None

def get_FRED_series():
    fr = Fred(api_key=FRED_API_Key, response_type='json')
    dfr = pd.read_json(fr.series.search('daily', response_type='json'))
    fids = []
    ftitles = []
    for i in range(len(dfr)):
        if '(DISCONTINUED)' not in dfr.iloc[i]['seriess']['title']:
            fids.append(dfr.iloc[i]['seriess']['id'])
            ftitles.append(dfr.iloc[i]['seriess']['title'])
    return pd.DataFrame(data={'Series ID': fids, 'Series Title': ftitles})

def dl_FRED(FRED_series, start_time):
    successes, failures = 0, 0
    print('Downloading FRED data...')
    for i, row in FRED_series.iterrows():
        time.sleep(0.5)
        fid, ftitle = row['Series ID'], row['Series Title']
        print('\n', i, '\n', fid, '\n', ftitle)
        if start_time:
            url = f'https://api.stlouisfed.org/fred/series/observations?    \
                    series_id={fid}&api_key={FRED_API_Key}&file_type=json&observation_start={start_time}'
        else:
            url = f'https://api.stlouisfed.org/fred/series/observations?    \
                    series_id={fid}&api_key={FRED_API_Key}&file_type=json'
        print("Acquiring:", ftitle)
        future = session.get(url)
        response = future.result()
        print(response)
        if response.status_code == 200:
            print('Acquired.')
            dfr = pd.read_json(response.content)
            dfi = pd.concat([dfr, dfr['observations'].apply(pd.Series)], axis = 1).drop('observations', axis = 1)
            if len(dfi):
                dfi = dfi[['date', 'value', 'units']]
                dfi['value'] = dfi['value'].apply(float_or_NaN)
                dfi.columns = ['date', ftitle, 'units']
                dfi['date'] = pd.to_datetime(dfi['date'], format='%Y-%m-%d')
                dfi.set_index('date', inplace=True)
                print("Updated.")
                successes += 1
                if successes == 1:
                    df_FRED_ = dfi
                else:
                    df_FRED_ = df_FRED_.merge(dfi, left_index=True, right_index=True, copy=False, how='outer')
            else:
                print("No update available.")
        else:
            print('Acquisition failed.')
            failures += 1
    else:
        print()
        print('Loop finished.')
        print(f'Acquired {successes} / {successes + failures}.')
    return df_FRED_ if successes else None

def get_data(ticker_cache_dir, AV_API_key, ticker, commodity_type, use_cache=False):
    try:
        if use_cache == True:
            # load from cache
            df = pd.read_csv(f'.\{ticker_cache_dir}\{ticker}.csv', index_col='date', parse_dates=True)
            print('Ticker data retrieved from cache.')
        else:
            raise Exception('Ignoring cache, downloading from API.')
            print('Ignoring cache, downloading from API.')
    except:
        # Download from AlphaVantage
        print('Acquiring ticker data...')
        if commodity_type not in ["Physical Currency", "Digital Currency"]:
            data, metadata = ts.get_daily(ticker,'full')
            df = pd.DataFrame(data).transpose().sort_index(axis=0 ,ascending=True).astype('float')
            df.columns = ['open', 'high', 'low', 'close', 'volume']
        
        elif commodity_type == "Physical Currency":
            data, metadata = fx.get_currency_exchange_daily(ticker, 'USD', 'full')
            df = pd.DataFrame(data).transpose().sort_index(axis=0 ,ascending=True).astype('float')
            df.columns = ['open', 'high', 'low', 'close']
            df['volume'] = 0.0
               
        else:
            data, metadata = cc.get_digital_currency_daily(ticker, 'USD')
            df = pd.DataFrame(data).transpose().sort_index(axis=0 ,ascending=True).iloc[:,[0,2,4,6,8,9]].astype('float')
            df.columns = ['open', 'high', 'low', 'close', 'volume', 'market_cap']
        print('Ticker data acquired.')
        
        # datetime index
        df.index.name = 'date'
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        
        # add a 1-period differenced column
        df['diff1'] = df['close'].diff()/df['close']
        
        # add calendrical categoricals
        for i in ['year', 'month', 'day', 'dayofweek', 'dayofyear', 'weekofyear', 'quarter']:
            df[i] = getattr(df.index, i)
            if np.int64(0) in list(df[i]):
                df[i] = df[i].apply(lambda x: str(int(x)))
            else:
                df[i] = df[i].apply(lambda x: str(int(x-1)))
                
        # compute MACD and candlesticks
        df['inc'] = df.close > df.open
        df['inc'] = df['inc'].apply(lambda bool: str(bool))
        df['ema12'] = EMA(12, df['open'])
        df['ema26'] = EMA(26, df['open'])
        df['macd'] = df['ema12'] - df['ema26']
        df['signal'] = EMA(9, df['macd'])
        df['zero'] = df['volume'].apply(lambda x: x*0)
        df['hist'] = df.macd - df.signal
        df['histc'] = df.macd > df.signal
        df['histc'] = df['histc'].apply(lambda bool: str(bool))
              
        # compute technical indicators from TA-Lib  
        inputs = df.loc[:, ['open', 'high', 'low', 'close', 'volume']]
        function_groups = talib.get_function_groups()
        functions = talib.get_functions()
        for function in functions:
            f = talib.abstract.Function(function)
            try:
                y = f(inputs)
                if function in function_groups['Pattern Recognition']:
                    d = {200:'++', 100:'+', 0:'0', -100:'-', -200:'--'}
                    df[pattern_dict[function]] = [d[i] for i in y]
                elif function == 'HT_PHASOR':
                    df['HT_PHASOR_I'], df['HT_PHASOR_Q'] = y['inphase'], y['quadrature']
                elif function == 'HT_SINE':
                    df['HT_SINE'], df['HT_LEADSINE'] = y['sine'], y['leadsine']
                elif function == 'MINMAX':
                    df['MIN'], df['MAX'] = y['min'], y['max']
                elif function == 'MINMAXINDEX':
                    df['MINIDX'], df['MAXIDX'] = y['minidx'], y['maxidx']
                elif  function == 'AROON':
                    df['AROON_DOWN'], df['AROON_UP'] = y['aroondown'], y['aroonup']
                elif function == 'MACD':
                    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = y['macd'], y['macdsignal'], y['macdhist']
                elif function == 'MACDEXT': # TODO allow custom periods
                    df['MACDext'], df['MACD_SIGNALext'], df['MACD_HISText'] = y['macd'], y['macdsignal'], y['macdhist']
                elif function == 'MACDFIX': # TODO allow custom periods
                    df['MACDfix'], df['MACD_SIGNALfix'], df['MACD_HISTfix'] = y['macd'], y['macdsignal'], y['macdhist']
                elif function == 'STOCH':
                    df['STOCH_slowk'], df['STOCH_slowd'] = y['slowk'], y['slowd']
                elif function == 'STOCHF':
                    df['STOCH_fastk'], df['STOCH_fastd'] = y['fastk'], y['fastd']
                elif function == 'STOCHRSI':
                    df['STOCHRSI_fastk'], df['STOCHRSI_fastd'] = y['fastk'], y['fastd']
                elif function == 'BBANDS':
                    df['BB_u'], df['BB_m'], df['BB_l'] = y['upperband'], y['middleband'], y['lowerband']
                elif function == 'MAMA':
                    df['MAMA'], df['FAMA'] = y['mama'], y['fama']
                else:
                    df[function] = y
            except:
                pass
        df.dropna(subset=['close'], inplace=True)
        # store df_ticker in cache
        if use_cache:
            df.to_csv(f'.\{ticker_cache_dir}\{ticker}.csv')
            print('Ticker data cached.')
    
    start_time = df.index[0].strftime(format='%Y-%m-%d')
    return df, start_time

def get_df_cat(df_ticker):
    categorical = ['inc', 'dayofweek', 'month', 'quarter','2 CROWS', '3 BLACK CROWS', '3 INSIDE', '3 LINE STRIKE',
               '3 OUTSIDE', '3 STARS IN THE SOUTH', '3 WHITE SOLDIERS', 'ABANDONED BABY', 'ADVANCE BLOCK', 'BELTHOLD', 'BREAKAWAY', 
               'CLOSING MARUBOZU', 'CONCEAL BABY SWALL', 'COUNTERATTACK', 'DARK CLOUD COVER',  'DOJI', 'DOJI STAR', 'DRAGONFLY DOJI', 
               'ENGULFING', 'EVENING DOJISTAR', 'EVENING STAR', 'GAP-SIDE SIDE-WHITE', 'GRAVESTONE DOJI',  'HAMMER', 'HANGINGMAN', 'HARAMI', 
               'HARAMI CROSS', 'HIGH WAVE', 'HIKKAKE', 'HIKKAKE MOD', 'HOMING PIGEON', 'HT_TRENDMODE', 'IDENTICAL 3 CROWS', 'IN-NECK', 
               'INVERTED HAMMER', 'KICKING', 'KICKING BY LENGTH', 'LADDER BOTTOM', 'LONG LINE', 'LONG-LEGGED DOJI', 'MARUBOZU', 
               'MATCHING LOW',  'MATHOLD', 'MORNING DOJI STAR', 'MORNING STAR', 'ON NECK', 'PIERCING', 'RICKSHAW MAN', 'RISE-FALL 3-METHODS',
               'SEPARATING LINES',  'SHOOTING STAR', 'SHORT LINE', 'SPINNING TOP', 'STALLED PATTERN', 'STICK SANDWICH', 'TAKURI', 
               'TASUKI GAP', 'THRUSTING',  'TRI-STAR', 'UNIQUE 3 RIVER', 'UP-SIDE GAP 2 CROWS', 'X-SIDE GAP 3 METHODS']
 
    df_cat = df_ticker.dropna(subset=['close'])[categorical]
    df_cat = df_cat.fillna(method='ffill')
    df_cat = df_cat.fillna(method='bfill')
    df_cat['HT_TRENDMODE'] = df_cat['HT_TRENDMODE'].apply(lambda x : str(x))   
    print()
    print(list(df_cat['HT_TRENDMODE'].unique()))
    print()

    for col in df_cat.columns:
        if (set(df_cat[col])) == {'False', 'True'}:
            df_cat[col] = df_cat[col].apply(lambda x: {'False':'0', 'True':'1'}[x])

    # setup df_pat for plotting P4    
    df_pat = df_cat[[cat for cat in categorical if cat not in ['inc', 'dayofweek', 'month', 'quarter']]].copy()
    df_pat['HT_TRENDMODE'] = df_pat['HT_TRENDMODE'].apply(lambda x: {'0':'--', '1':'++'}[x])
    df_pat = pd.DataFrame(df_pat.stack(), columns=['signal']).reset_index()
    color_dict = {'--':'red', '-':'lightcoral', '0':'white', '+':'lightgreen', '++':'green'}
    df_pat['color']=df_pat['signal'].apply(lambda x: color_dict[x])

    for col in df_cat.columns:
        if col not in ['day','dayofweek', 'dayofyear', 'month', 'quarter', 'year']:
            df_cat[col+'-1'] = df_cat[col].shift(+1)
            df_cat[col+'-2'] = df_cat[col].shift(+2)
            df_cat[col+'-3'] = df_cat[col].shift(+3)

    df_cat['inc+1'] = df_cat['inc'].shift(-1) # target
    df_cat = df_cat.dropna()   
    
    return df_cat, df_pat

def get_ML_ab(df_cat, train_a, train_b, n_projections):
    df = df_cat.copy()
    y = df['inc+1'] # target
    df = df.drop(columns=['inc+1']) # target removed
    
    # OHE
    for col in df.columns:
        if len(set(df[col])) == 1 or '0' not in set(df[col]):
            df.drop(columns=[col], inplace=True)
    le = LabelEncoder()
    y = le.fit_transform(y)
    enc = OneHotEncoder(handle_unknown='error', drop=['0']*len(df.columns), sparse=True)
    X = enc.fit_transform(df)
    
    print('ok1')
    # split
    end_ind = min(len(df), train_b + n_projections)
    X_train, X_test = X[train_a:train_b,:], X[train_b:end_ind,:]
    y_train, y_test = y[train_a:train_b], y[train_b:end_ind]
    test_dates = df_cat.index[train_b:end_ind].strftime('%Y-%m-%d')
    print('ok2')

    # classify
    predictions = {}
    predictions['Date'] = test_dates
    predictions['Target'] = y_test
    for classifier_name, classifier in list(dict_classifiers.items())[:11]:       
        if classifier_name not in dense:
            classifier.fit(X_train, y_train)
            yhat = classifier.predict(X_test)
        else:
            classifier.fit(X_train.toarray(), y_train)
            yhat = classifier.predict(X_test.toarray())
        predictions[classifier_name] = yhat
    print('ok3')
    df_ML = pd.DataFrame(predictions)
    return df_ML

def get_ARIMA_ab(df_ticker, train_a, train_b, forecast_length=5, n_projections=10):
    
    df_ARIMA = df_ticker[['close', 'diff1']].copy()
    full_series_length = len(df_ARIMA)
    seriest = df_ARIMA['close']
    seriesi = seriest.reset_index(drop=True)
    aa_kwargs = {'start_p':1, 'start_q':1, 'max_p':3, 'max_q':3, 
                 'm':7, 'start_P':0, 'start_Q':1, 'seasonal':True,
                 'd':None, 'D':1, 'trace':True, 'error_action':'ignore', 
                 'suppress_warnings':True, 'stepwise':True, 'njobs':6}
    
    model = pm.auto_arima(seriesi.iloc[train_a:train_b], **aa_kwargs)
    print('SARIMAX hyperparameters determined.')
    model_kwargs = model.arima_res_._init_kwds.copy()
    model_params = model.params()
    start_params = model_params

    fc_cols = [e for t in [(f't+{i}_ciL', f't+{i}_ciU', f't+{i}_FC', f't+{i}_dt') 
                       for i in range(1, forecast_length + 1)] for e in t]
    df_ARIMA = pd.concat([df_ARIMA, pd.DataFrame(columns=fc_cols)], sort=False)
    dates = pd.date_range(df_ARIMA.index[-1], periods=forecast_length+1, freq='B')[1:]
    idx = df_ARIMA.index.append(dates)
    df_ARIMA = df_ARIMA.reindex(idx)
    df_ARIMA.index.name = 'date'
    print('Training and forecasting sliding window models...')
    for k in range(0, min(n_projections, len(seriesi)-train_b)):
        mod = sm.tsa.statespace.SARIMAX(endog=seriesi.iloc[train_a+k:train_b+k], **model_kwargs)
        try:
            fit_res = mod.fit(start_params=start_params, disp=0)
        except:
            pass
        # will use previous fit's values if fit fails
        forecast = fit_res.get_forecast(steps=forecast_length)
        ci = forecast.conf_int()
        ci['mean']=forecast.predicted_mean
        ci['trained_w']=seriest.index[train_b+k-1]
        start_params = fit_res.params
        
        for i in range(forecast_length):
            df_ARIMA.at[df_ARIMA.index[train_b+k+i], f't+{i+1}_ciL'] = ci.iloc[i]['lower close']
            df_ARIMA.at[df_ARIMA.index[train_b+k+i], f't+{i+1}_ciU'] = ci.iloc[i]['upper close']
            df_ARIMA.at[df_ARIMA.index[train_b+k+i], f't+{i+1}_FC'] = ci.iloc[i]['mean']
            df_ARIMA.at[df_ARIMA.index[train_b+k+i], f't+{i+1}_dt'] = ci.iloc[i]['trained_w']

    for i in range(forecast_length):
        df_ARIMA[f't+{i+1}_PE'] =     ( df_ARIMA[f't+{i+1}_FC'] - df_ARIMA['close'] ) / df_ARIMA['close']
        df_ARIMA[f't+{i+1}_PE_ciL'] = ( df_ARIMA[f't+{i+1}_ciL'] - df_ARIMA['close'] ) / df_ARIMA['close']
        df_ARIMA[f't+{i+1}_PE_ciU'] = ( df_ARIMA[f't+{i+1}_ciU'] - df_ARIMA['close'] ) / df_ARIMA['close']
       
    # This would be a good time to cache the dataframe .....
    # df_ARIMA.to_csv(f'.\{ticker_cache_dir}\{ticker}_ARIMA_{train_a}-{train_b}.csv')
    print('ARIMA models trained and forecasted')
    return df_ARIMA

def get_df_hist(df_ARIMA):
    
    def get_hist(col):
        hist, edges = np.histogram(df_ARIMA[col].dropna(), 
                                bins=10, density=True)
        top, bottom, left, right = hist, [0]*10, edges[:-1], edges[1:]
        return top, bottom, left, right
    
    ddict = defaultdict(list)
    for col in ['t+5_PE', 't+4_PE', 't+3_PE', 't+2_PE', 't+1_PE', 'diff1']:
        top, bottom, left, right = get_hist(col)
        ddict['col'].append([col]*10)
        ddict['top'].append(list(top))
        ddict['bottom'].append(bottom)
        ddict['left'].append(list(left))
        ddict['right'].append(list(right))
    ddict = {k:[e for l in v for e in l] for k,v in ddict.items()}
    df_hist = pd.DataFrame(ddict)
    return df_hist

def get_df_hist2(df_ARIMA):
    ddict2 = defaultdict(list)
    for col, clr in zip(['t+5_PE', 't+4_PE', 't+3_PE', 't+2_PE', 't+1_PE', 'diff1'],
                        ['orange', 'yellow', 'green', 'blue', 'purple', 'red']):
        ecdf = ECDF(df_ARIMA[col].dropna())
        x, y = ecdf.x[abs(ecdf.x) < 100], ecdf.y[abs(ecdf.x) < 100]
        colname, clrname = [col]*len(x), [clr]*len(x)
        ddict2['x'].append(x)
        ddict2['y'].append(y)
        ddict2['col'].append(colname)
        ddict2['clr'].append(clrname)
    ddict2 = {k:[e for l in v for e in l] for k,v in ddict2.items()}
    df_hist2 = pd.DataFrame(ddict2)
    return df_hist2

def modify_doc(doc):
    
    # Make widgets
    type_picker = Select(title="Type", value="S&P500", 
                         options=["Digital Currency", 
                                  "Physical Currency", 
                                  "S&P500", 
                                  "NYSE Equity", 
                                  "NASDAQ Equity", 
                                  "AMEX Equity"])
    
    stock_picker = Select(title="Select a Stock",  
                          value=df_0['name'][0], 
                          options=df_0[df_0['type']=="S&P500"]['name'].tolist())
    
    year_picker = Select(title="Select a Year",  
                         value="2018", 
                         options=[str(i) for i in range(2008,2019)], 
                         width=100)
    
    month_picker = Select(title="Select a Month",  
                          value="January", 
                          options=months, 
                          width=150)

    reset_button = Button(label='Full History')
    
    c = column(Div(text="", height=8), 
               reset_button, 
               width=100)

    # Setup data
    df_ticker, start_time = get_data(ticker_cache_dir, AV_API_key, 
                                     ticker, commodity_type, use_cache=False)
    source = ColumnDataSource(data=df_ticker)

    df_cat, df_pat = get_df_cat(df_ticker)
    source_pat = ColumnDataSource(df_pat)

    # Setup forecasts
    series_length = len(df_ticker) 
    train_a, train_b = series_length-40, series_length-10
    forecast_length, n_projections = 5, 10

    df_ARIMA = get_ARIMA_ab(df_ticker, train_a, train_b, 
                            forecast_length=forecast_length, 
                            n_projections=n_projections)   
    sourceA = ColumnDataSource(data=df_ARIMA)

    df_hist = get_df_hist(df_ARIMA)
    source_hist = ColumnDataSource(data=df_hist)

    df_hist2 = get_df_hist2(df_ARIMA)
    source_hist2 = ColumnDataSource(data=df_hist2)

    df_ML = get_ML_ab(df_cat, train_a, train_b, n_projections=n_projections)
    source_ML = ColumnDataSource(data=df_ML)
    
    ########################
    ###### Setup Plots #####
    ########################

    width_ms = 12*60*60*1000 # half day in ms
    color_mapper = CategoricalColorMapper(factors=["True", "False"], 
                                          palette=["green", "red"])
    # Make P1 Plot (Candlesticks)
    def makeP1():
        p1 = figure(plot_height=400, x_axis_type="datetime", tools="xwheel_pan,xwheel_zoom,pan,box_zoom", active_scroll='xwheel_zoom')
        bst = p1.add_tools(BoxSelectTool(dimensions="width"))
        # Create price glyphs and volume glyph
        p1O = p1.line(x='date', y='open', source=source, color=Spectral5[0], alpha=0.8, legend="OPEN")
        p1C = p1.line(x='date', y='close', source=source, color=Spectral5[1], alpha=0.8, legend="CLOSE")
        p1L = p1.line(x='date', y='low', source=source, color=Spectral5[4], alpha=0.8, legend="LOW")
        p1H = p1.line(x='date', y='high', source=source, color=Spectral5[3], alpha=0.8, legend="HIGH")   
        p1.line(x='date', y='ema12', source=source, color="magenta", legend="EMA-12")
        p1.line(x='date', y='ema26', source=source, color="black", legend="EMA-26")
        p1.segment(x0='date', y0='high', x1='date', y1='low', color={'field': 'inc', 'transform': color_mapper}, source=source)
        p1.vbar(x='date', width=width_ms, top='open', bottom='close', color={'field': 'inc', 'transform': color_mapper}, source=source)
        # Add axis labels
        p1.yaxis.axis_label = '\n \n \n \n \n \n \n \n Price ($USD/share)'
        # Add legend
        p1.legend.orientation = 'horizontal'
        p1.legend.title = 'Daily Stock Price'
        p1.legend.click_policy="hide"
        p1.legend.location="top_left"
        # Add HoverTools
        p1.add_tools(HoverTool(tooltips=[('Date','@date{%F}'),('Open','@open{($ 0.00)}'),('Close','@close{($ 0.00)}'),
                                        ('Low','@low{($ 0.00)}'),('High','@high{($ 0.00)}'),('Volume','@volume{(0.00 a)}')],
                               formatters={'date': 'datetime'},mode='mouse'))
        p1.toolbar.logo = None
        # Formatting
        p1.yaxis[0].formatter = NumeralTickFormatter(format="$0.00")
        p1.outline_line_width = 1
        return p1
    p1 = makeP1()

    # Make P2 Plot (Volume)
    def makeP2():
        p2 = figure(plot_height=150, x_axis_type="datetime", x_range=p1.x_range, tools="xwheel_pan,xwheel_zoom,pan,box_zoom", active_scroll='xwheel_pan')
        p2V = p2.varea(x='date', y1='volume', y2='zero', source=source, color="black", alpha=0.8)
        p2.add_tools(HoverTool(tooltips=[('Date','@date{%F}'),('Open','@open{($ 0.00)}'),('Close','@close{($ 0.00)}'),
                                        ('Low','@low{($ 0.00)}'),('High','@high{($ 0.00)}'),('Volume','@volume{(0.00 a)}')],
                            formatters={'date': 'datetime'},mode='mouse'))
        p2.toolbar.logo = None
        p2.xaxis.axis_label = 'Date'
        p2.yaxis.axis_label = '\n \n \n \n \n Volume (shares)'
        p2.yaxis[0].formatter = NumeralTickFormatter(format="0.0a")
        p2.outline_line_width = 1
        return p2
    p2 = makeP2()

    # Make P3 Plot (MACD-Signal) 
    def makeP3():
        p3 = figure(plot_height=150, x_axis_type="datetime", x_range=p1.x_range, tools="xwheel_pan,xwheel_zoom,pan,box_zoom", active_scroll='xwheel_pan')   
        p3.line(x='date', y='macd', source=source, color="green", legend="-MACD")
        p3.line(x='date', y='signal', source=source, color="red", legend="-Signal")
        p3.vbar(x='date', top='hist', source=source, width=width_ms, color={'field': 'histc', 'transform': color_mapper}, alpha=0.5)
        # Add HoverTools
        p3.add_tools(HoverTool(tooltips=[('Date','@date{%F}'),('EMA-12','@ema12{($ 0.00)}'),('EMA-26','@ema26{($ 0.00)}'),
                                        ('MACD','@macd{($ 0.00)}'),('Signal','@signal{($ 0.00)}')],
                            formatters={'date': 'datetime'},mode='mouse'))
        p3.toolbar.logo = None
        # Add legend
        p3.legend.orientation = 'horizontal'
        p3.legend.location="top_left"
        p3.legend.orientation = 'horizontal'
        p3.legend.title = 'Moving Average Convergence Divergence'
        p3.legend.location="top_left"
        p3.legend.label_text_font_size = '12pt'
        p3.legend.glyph_height = 1 #some int
        #p3.legend.glyph_width = 12 #some int
        # Add axis labels
        p3.yaxis.axis_label = '\n \n \n \n \n Indicator ($USD)'
        # Add tick formatting
        p3.yaxis[0].formatter = NumeralTickFormatter(format="$0.00")
        p3.outline_line_width = 1
        return p3
    p3 = makeP3()

    # Make P4 Plot (Price-Action Event Indicators)
    def makeP4():          
        df_pat = df_ticker[[col for col in pattern_dict.values()]]
        df_pat.columns.name = 'pattern'
   
        # D, L sort event types so 
        # the most common events are at top of plot
        D = {col:df_pat[col].value_counts().to_dict()['0'] 
                 for col in df_pat.columns}
        
        L = [i[0] for i in sorted(D.items(), 
                                  key=lambda kv:(kv[1], kv[0]), 
                                  reverse=True)]
        
        df_pat['HT_TRENDMODE'] = df_cat['HT_TRENDMODE'].apply(lambda x: {'0':'--', '1':'++'}[x])
        df_pat2 = pd.DataFrame(df_pat.stack(), columns=['signal']).reset_index()
        color_dict = {'--':'red', '-':'lightcoral', '0':'white', '+':'lightgreen', '++':'green'}
        df_pat2['color']=df_pat2['signal'].apply(lambda x: color_dict[x])
        source_pat2 = ColumnDataSource(df_pat2)
              
        p4 = figure(plot_width=800, plot_height=800, y_range=L,
                    x_axis_location="above", x_axis_type="datetime", 
                    x_range=p1.x_range)
        
        p4.rect(x="date", y="pattern", width=24*60*60*1000, height=1, 
                source=source_pat2, line_color=None, line_width=0.2, 
                fill_color='color')
        return p4
    p4 = makeP4()

    ind_end = min(len(df_ARIMA) -1 , train_b + n_projections + forecast_length + 30)    
    # Make P21 Plot (ARIMA Training - Price)
    def make_P21():
        p21 = figure(plot_width=600, plot_height=250, x_axis_type="datetime",
                     tools="xwheel_pan,xwheel_zoom,pan,box_zoom", active_scroll='xwheel_zoom')
        p21.scatter(x='date', y='t+5_FC', source=sourceA, color='orange', alpha=0.1, legend='T+5')
        p21.varea(x='date', y1='t+5_ciU', y2='t+5_ciL', source=sourceA, color='orange', alpha=0.1, legend='T+5')
        p21.scatter(x='date', y='t+4_FC', source=sourceA, color='yellow', alpha=0.1, legend='T+4')
        p21.varea(x='date', y1='t+4_ciU', y2='t+4_ciL', source=sourceA, color='yellow', alpha=0.1, legend='T+4')
        p21.scatter(x='date', y='t+3_FC', source=sourceA, color='green', alpha=0.1, legend='T+3')
        p21.varea(x='date', y1='t+3_ciU', y2='t+3_ciL', source=sourceA, color='green', alpha=0.1, legend='T+3')
        p21.scatter(x='date', y='t+2_FC', source=sourceA, color='blue', alpha=0.1, legend='T+2')
        p21.varea(x='date', y1='t+2_ciU', y2='t+2_ciL', source=sourceA, color='blue', alpha=0., legend='T+2')
        p21.scatter(x='date', y='t+1_FC', source=sourceA, color='purple', alpha=0.1, legend='T+1')
        p21.varea(x='date', y1='t+1_ciU', y2='t+1_ciL', source=sourceA, color='purple', alpha=0.1, legend='T+1')
        p21.line(x='date', y='close', source=sourceA, color='black', legend='ACTUAL')
        p21.yaxis.axis_label = 'Price ($USD/Share)'
        p21.xaxis.axis_label = 'Date'
        p21.legend.title = 'Forecast'
        p21.legend.location = 'top_left'
        p21.x_range = Range1d(df_ARIMA.index[max(0, train_a - 10)], df_ARIMA.index[ind_end])
        cols=['t+5_ciU', 't+5_ciL', 'close']
        ymin=0.9 * df_ARIMA[cols].iloc[max(0, train_a - 10):ind_end].min().min()
        ymax=1.1 * df_ARIMA[cols].iloc[max(0, train_a - 10):ind_end].max().max()
        p21.y_range = Range1d(ymin, ymax)
        box21 = BoxAnnotation(left=df_ARIMA.index[train_a], right=df_ARIMA.index[train_b - 1], fill_color='red', fill_alpha=0.1)
        p21.add_layout(box21)
        return p21, box21
    p21, box21 = make_P21()

    # Make P22 Plot (ARIMA Training - Price Diff)
    def make_P22():
        p22 = figure(plot_width=600, plot_height=250, x_axis_type="datetime", x_range=p21.x_range,
                     tools="xwheel_pan,xwheel_zoom,pan,box_zoom", active_scroll='xwheel_pan')
        
        p22.varea(x='date', y1='t+5_PE_ciU', y2='t+5_PE_ciL', source=sourceA, color='orange', alpha=0.1, legend='T+5')
        p22.line(x='date', y='t+5_PE', source=sourceA, color='orange', alpha=0.1, legend='T+5')
        p22.scatter(x='date', y='t+5_PE', source=sourceA, color='orange', alpha=0.1, legend='T+5')
        p22.varea(x='date', y1='t+4_PE_ciU', y2='t+4_PE_ciL', source=sourceA, color='yellow', alpha=0.1, legend='T+4')
        p22.line(x='date', y='t+4_PE', source=sourceA, color='yellow', alpha=0.1, legend='T+4')
        p22.scatter(x='date', y='t+4_PE', source=sourceA, color='yellow', alpha=0.1, legend='T+4')
        p22.varea(x='date', y1='t+3_PE_ciU', y2='t+3_PE_ciL', source=sourceA, color='green', alpha=0.1, legend='T+3')
        p22.line(x='date', y='t+3_PE', source=sourceA, color='green', alpha=0.1, legend='T+3')
        p22.scatter(x='date', y='t+3_PE', source=sourceA, color='green', alpha=0.1, legend='T+3')
        p22.varea(x='date', y1='t+2_PE_ciU', y2='t+2_PE_ciL', source=sourceA, color='blue', alpha=0.1, legend='T+2')
        p22.line(x='date', y='t+2_PE', source=sourceA, color='blue', alpha=0.1, legend='T+2')
        p22.scatter(x='date', y='t+2_PE', source=sourceA, color='blue', alpha=0.1, legend='T+2')
        p22.varea(x='date', y1='t+1_PE_ciU', y2='t+1_PE_ciL', source=sourceA, color='purple', alpha=0.1, legend='T+1')
        p22.line(x='date', y='t+1_PE', source=sourceA, color='purple', alpha=0.1, legend='T+1')
        p22.scatter(x='date', y='t+1_PE', source=sourceA, color='purple', alpha=0.1, legend='T+1')
        # let's make a comparison: what are the corresponding PE's from the "day-behind" model
        p22.line(x='date', y='diff1', source=sourceA, color='red', alpha=0.4, legend='yest')
        
        p22.yaxis.axis_label = 'Error'
        p22.xaxis.axis_label = 'Date'
        p22.legend.title = 'Forecast'
        p22.legend.location = 'top_left'
        cols=['t+5_PE_ciU', 't+5_PE_ciL', 'diff1']
        p22.y_range = Range1d(1.1 * df_ARIMA[cols].iloc[max(0, train_a - 10):ind_end].min().min(),
                            1.1 * df_ARIMA[cols].iloc[max(0, train_a - 10):ind_end].max().max())
        box22 = BoxAnnotation(left=df_ARIMA.index[train_a], right=df_ARIMA.index[train_b - 1], fill_color='red', fill_alpha=0.1)
        p22.add_layout(box21)
        return p22, box22
    p22, box22 = make_P22()
      
    # Make P23 Plot (ARIMA Error - Dist)
    def make_P23():
        # Make CDSviews for each forecast set
        view5 = CDSView(source=source_hist,
                        filters=[GroupFilter(column_name='col', group='t+5_PE')])
        view4 = CDSView(source=source_hist,
                        filters=[GroupFilter(column_name='col', group='t+4_PE')])
        view3 = CDSView(source=source_hist,
                        filters=[GroupFilter(column_name='col', group='t+3_PE')])
        view2 = CDSView(source=source_hist,
                        filters=[GroupFilter(column_name='col', group='t+2_PE')])
        view1 = CDSView(source=source_hist,
                        filters=[GroupFilter(column_name='col', group='t+1_PE')])
        viewD = CDSView(source=source_hist,
                        filters=[GroupFilter(column_name='col', group='diff1')])
        
        p23 = figure(plot_height=250, plot_width=200)
        
        p23.quad(source=source_hist, view=view5, top='top', bottom='bottom', 
                left='left', right='right', fill_color='orange', 
                line_color="white", alpha=0.1)

        p23.quad(source=source_hist, view=view4, top='top', bottom='bottom', 
                left='left', right='right', fill_color='yellow', 
                line_color="white", alpha=0.1)

        p23.quad(source=source_hist, view=view3, top='top', bottom='bottom', 
                left='left', right='right', fill_color='green', 
                line_color="white", alpha=0.1)
                
        p23.quad(source=source_hist, view=view2, top='top', bottom='bottom', 
                left='left', right='right', fill_color='blue', 
                line_color="white", alpha=0.1)

        p23.quad(source=source_hist, view=view1, top='top', bottom='bottom', 
                left='left', right='right', fill_color='purple', 
                line_color="white", alpha=0.1)

        p23.quad(source=source_hist, view=viewD, top='top', bottom='bottom', 
                left='left', right='right', fill_color="purple", 
                fill_alpha=0, line_color="red", alpha=1)
        p23.xaxis.axis_label = 'Error'
        return p23
    p23 = make_P23()

    #Make P24 Plot (ARIMA Error - CumDist)
    def make_P24():
        # Make CDSviews for each forecast set
        view5_2 = CDSView(source=source_hist2,
                        filters=[GroupFilter(column_name='col', group='t+5_PE')])
        view4_2 = CDSView(source=source_hist2,
                        filters=[GroupFilter(column_name='col', group='t+4_PE')])
        view3_2 = CDSView(source=source_hist2,
                        filters=[GroupFilter(column_name='col', group='t+3_PE')])
        view2_2 = CDSView(source=source_hist2,
                        filters=[GroupFilter(column_name='col', group='t+2_PE')])
        view1_2 = CDSView(source=source_hist2,
                        filters=[GroupFilter(column_name='col', group='t+1_PE')])
        viewD_2 = CDSView(source=source_hist2,
                        filters=[GroupFilter(column_name='col', group='diff1')])
        
        # panel showing empCDF of forecast and diff1
        p24 = figure(plot_height=250, plot_width=200)
        p24.line(source=source_hist2, view=view5_2, x='x', y = 'y', color='orange')
        p24.line(source=source_hist2, view=view4_2, x='x', y = 'y', color='yellow')
        p24.line(source=source_hist2, view=view3_2, x='x', y = 'y', color='green')
        p24.line(source=source_hist2, view=view2_2, x='x', y = 'y', color='blue')
        p24.line(source=source_hist2, view=view1_2, x='x', y = 'y', color='purple')
        p24.line(source=source_hist2, view=viewD_2, x='x', y = 'y', color='red')
        p24.xaxis.axis_label = 'Error'
        return p24
    p24 = make_P24()

    # Make Bokeh DataTable from ML predictions df
    def make_PT():
        columns = [TableColumn(field=col, title=col) 
                          for col in df_ML.columns]                  
        pT = DataTable(source=source_ML, columns=columns, 
                       editable=False, width=800, height=200)
        return pT
    pT = make_PT()
    
    #######################
    ###### Callbacks ######
    #######################

    #Define JavaScript callbacks
    JS = '''
        clearTimeout(window._autoscale_timeout);

        var date = source.data.date,
            low = source.data.low,
            high = source.data.high,
            volume = source.data.volume,
            macd = source.data.macd,
            start = cb_obj.start,
            end = cb_obj.end,
            min1 = Infinity,
            max1 = -Infinity,
            min2 = Infinity,
            max2 = -Infinity,
            min3 = Infinity,
            max3 = -Infinity;

        for (var i=0; i < date.length; ++i) {
            if (start <= date[i] && date[i] <= end) {
                max1 = Math.max(high[i], max1);
                min1 = Math.min(low[i], min1);
                max2 = Math.max(volume[i], max2);
                min2 = Math.min(volume[i], min2);
                max3 = Math.max(macd[i], max3);
                min3 = Math.min(macd[i], min3);
            }
        }
        var pad1 = (max1 - min1) * .05;
        var pad2 = (max2 - min2) * .05;
        var pad3 = (max3 - min3) * .05;

        window._autoscale_timeout = setTimeout(function() {
            y1_range.start = min1 - pad1;
            y1_range.end = max1 + pad1;
            y2_range.start = min2 - pad2;
            y2_range.end = max2 + pad2;
            y3d = Math.max(Math.abs(min3 - pad3), Math.abs(max3 + pad3))
            y3_range.start = -y3d;
            y3_range.end = y3d;
        });
    '''
    callbackJS = CustomJS(args={'y1_range': p1.y_range, 
                                'y2_range': p2.y_range, 
                                'y3_range': p3.y_range, 
                                'source': source}, code=JS)
    p1.x_range.js_on_change('start', callbackJS)
    p1.x_range.js_on_change('end', callbackJS)

    # reset history button
    reset_button.js_on_click(CustomJS(args=dict(p1=p1, p2=p2), code="""
    p1.reset.emit()
    p2.reset.emit()
    """))

    # Define Python callbacks
    def update_bst(attrname, old, new):
        print('updating bst')
        r = source.selected.indices
        train_a, train_b = min(r), max(r)
        
        # retrain and update predictions
        print('retraining ARIMA')
        df_ARIMA = get_ARIMA_ab(df_ticker, train_a, train_b, 
                                forecast_length=5, n_projections=n_projections)
        sourceA.data = ColumnDataSource(df_ARIMA).data
        
        df_hist = get_df_hist(df_ARIMA)
        source_hist.data = ColumnDataSource(data=df_hist).data

        df_hist2 = get_df_hist2(df_ARIMA)
        source_hist2.data = ColumnDataSource(data=df_hist2).data
        
        print('refitting ML')
        df_ML = get_ML_ab(df_cat, train_a, train_b, 
                          n_projections=n_projections)
        source_ML.data = ColumnDataSource(data=df_ML).data
 
        ind_end = min(len(df_ARIMA) - 1, train_b + n_projections + forecast_length + 30) 
        # update p21 plot
        print('updating p21')
        p21.x_range.start = df_ARIMA.index[max(0, train_a - 10)]
        p21.x_range.end = df_ARIMA.index[ind_end]
        cols=['t+5_ciU', 't+5_ciL', 'close']
        ymin=0.9 * df_ARIMA[cols].iloc[max(0, train_a - 10):
                                       ind_end].min().min()
        ymax=1.1 * df_ARIMA[cols].iloc[max(0, train_a - 10):
                                       ind_end].max().max()
        p21.y_range.start = ymin
        p21.y_range.end =  ymax
        box21.left = df_ARIMA.index[train_a]
        box21.right = df_ARIMA.index[train_b - 1]
        
        # update p22 plot
        print('updating p22')
        cols=['t+5_PE_ciU', 't+5_PE_ciL', 'diff1']
        p22.y_range.start = 1.1 * df_ARIMA[cols].iloc[max(0, train_a - 10):
                                                      ind_end].min().min()
        p22.y_range.end =   1.1 * df_ARIMA[cols].iloc[max(0, train_a - 10):
                                                      ind_end].max().max()
        box22.left = df_ARIMA.index[train_a]
        box22.right = df_ARIMA.index[train_b - 1]

    def update_widget(attrname, old, new):
        commodity_type = type_picker.value
        stock_picker.options = df_0[df_0['type']==commodity_type]['name'].tolist()
    
    def update_data(attrname, old, new):
        # Get the current Select value
        commodity_type = type_picker.value
        print('type:', commodity_type)
        ticker = df_0.loc[df_0['name'] == stock_picker.value, 'code'].iloc[0]
        print('ticker:', ticker)
 
        # Get the new data
        df_ticker, start_time = get_data(ticker_cache_dir, AV_API_key, ticker, commodity_type, use_cache=False)
        source.data = ColumnDataSource(data=df_ticker).data
        
        df_cat, df_pat = get_df_cat(df_ticker)
        source_pat.data = ColumnDataSource(df_pat).data
        
        p1.x_range.start = df_ticker.index[0]
        p1.x_range.end = df_ticker.index[-1]
        reset_on_update=True
        if reset_on_update:
            CustomJS(args=dict(p1=p1, p2=p2), code="""p1.reset.emit()
                                                      p2.reset.emit()""")
        
    def update_axis(attrname, old, new):
        # Get the current Select values
        source.data = ColumnDataSource(data=df_ticker).data
        year = year_picker.value
        month = f'{months.index(month_picker.value) + 1:02d}'   
        start = datetime.strptime(f'{year}-{month}-01', "%Y-%m-%d")
        if month == '12':
            end = datetime.strptime(f'{str(int(year)+1)}-01-01', "%Y-%m-%d")
        else:
            end = datetime.strptime(f'{year}-{int(month)+1:02d}-01', "%Y-%m-%d")     
        p1.x_range.start = start
        p1.x_range.end = end
        # dfi = df_ticker.set_index(['date'])
        p1.y_range.start = df_ticker.loc[end:start]['low'].min()*0.95
        p1.y_range.end = df_ticker.loc[end:start]['high'].max()*1.05
        p2.y_range.start = df_ticker.loc[end:start]['volume'].min()*0.95
        p2.y_range.end = df_ticker.loc[end:start]['volume'].max()*1.05
        p3.y_range.start = df_ticker.loc[end:start]['macd'].min()*0.75
        p3.y_range.end = df_ticker.loc[end:start]['macd'].max()*1.25

    # Route Python callbacks
    source.selected.on_change('indices', update_bst)
    type_picker.on_change('value', update_widget)
    stock_picker.on_change('value', update_data)
    year_picker.on_change('value', update_axis)
    month_picker.on_change('value', update_axis)
    
    # Set up layouts and add to document
    row1 = row(type_picker, stock_picker, year_picker, month_picker, c,
               height=65, width=800, sizing_mode='stretch_width')
    row2 = row(p1, width=800, height=400, sizing_mode='stretch_width')
    row3 = row(p2, width=800, height=150, sizing_mode='stretch_width')
    row4 = row(p3, width=800, height=150, sizing_mode='stretch_width')
    row5 = row(p4, width=800, height=800, sizing_mode='stretch_width')
    row6 = row(p21, p23, width=800, height=250, sizing_mode='stretch_width')
    row7 = row(p22, p24, width=800, height=250, sizing_mode='stretch_width')
    row8 = row(pT, width=800, height=800, sizing_mode='stretch_width')
    layout = column(row1, row2, row4, row3, row5, row6, row7, row8,
                    width=800, height=2265, sizing_mode='stretch_both')
    doc.add_root(layout)

modify_doc(curdoc())