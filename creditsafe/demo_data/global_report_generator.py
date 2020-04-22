import pycountry

# Add countries for demo
CURRENCY_BY_COUNTRY_CODE = {
    'BE': 'EUR',
    'CY': 'EUR',
    'EE': 'EUR',
    'FI': 'EUR',
    'FR': 'EUR',
    'DE': 'EUR',
    'GR': 'EUR',
    'IE': 'EUR',
    'IT': 'EUR',
    'LV': 'EUR',
    'LT': 'EUR',
    'LU': 'EUR',
    'MC': 'EUR',
    'ME': 'EUR',
    'NL': 'EUR',
    'PT': 'EUR',
    'SK': 'EUR',
    'SI': 'EUR',
    'ES': 'EUR',
    'US': 'USD',
    'CH': 'CHF',
    'CA': 'CAD',
    'BR': 'BRL',
    'AE': 'AED',
    'AR': 'ARS',
    'CN': 'CNY',
    'MX': 'MXN',
    'SE': 'SEK',
    'NO': 'NOK',
    'RO': 'RON',
    'RU': 'RUB',
    'DK': 'DKK',
    'JP': 'JPY'
}


def get_report(creditsafe_id, country_alpha_3):
    country_alpha_2 = pycountry.countries.get(alpha_3=country_alpha_3).alpha_2
    currency = CURRENCY_BY_COUNTRY_CODE.get(country_alpha_2, None)
    return {
        "companyId": creditsafe_id,
        "dateOfOrder": "2020-04-21T13:19:43.958Z",
        "language": "en",
        "orderId": "N/A",
        "report": {
            "additionalInformation": {
                "additionalFinancials": [
                    {
                        "auditedAccounts": "Yes",
                        "auditorComments": "-",
                        "yearEndDate": "2010-08-31T00:00:00Z"
                    },
                    {
                        "auditedAccounts": "Yes",
                        "auditorComments": "-",
                        "yearEndDate": "2009-08-31T00:00:00Z"
                    },
                    {
                        "auditedAccounts": "Yes",
                        "auditorComments": "-",
                        "yearEndDate": "2008-08-31T00:00:00Z"
                    },
                    {
                        "auditedAccounts": "Yes",
                        "auditorComments": "-",
                        "yearEndDate": "2007-08-31T00:00:00Z"
                    },
                    {
                        "auditedAccounts": "Yes",
                        "auditorComments": "-",
                        "yearEndDate": "2006-08-31T00:00:00Z"
                    }
                ],
                "companyHistory": [
                    {
                        "date": "2015-04-24T00:00:00Z",
                        "description": "Group Structure Change"
                    }
                ],
                "industryComparison": {
                    "activityDescription": "Industry unknown",
                    "industryAverageCreditLimit": 2000.0,
                    "industryAverageCreditRating": "64"
                },
                "misc": {
                    "negativeRating": "-2",
                    "registeredForEmployeeTax": "false",
                    "registeredForFTax": "false",
                    "registeredForVat": "false"
                }
            },
            "companyId": creditsafe_id,
            "companyIdentification": {
                "activityClassifications": [
                    {
                        "classification": "SNI 2007"
                    }
                ],
                "basicInformation": {
                    "businessName": "Aerial Traders",
                    "companyRegistrationDate": "1957-01-11T00:00:00Z",
                    "companyRegistrationNumber": "5560642554",
                    "companyStatus": {
                        "description": "Active",
                        "status": "Active"
                    },
                    "contactAddress": {
                        "city": "ÄLMHULT",
                        "postalCode": "343 81",
                        "province": "KRONOBERG",
                        "simpleValue": "Box 700, 343 81 ÄLMHULT, KRONOBERG",
                        "street": "Box 700"
                    },
                    "country": country_alpha_2,
                    "legalForm": {
                        "description": "Limited liability company",
                        "providerCode": "AB"
                    },
                    "principalActivity": {
                        "description": "Föremålet för bolagets verksamhet är att självt eller genom  dotterbolag tillverka, inköpa och försälja varor för hem, hushåll och fritid, att äga och hyra ut industriell utrustning  huvudsakligen inom tillverkningsindustrin såsom möbelindustrin,"
                    },
                    "registeredCompanyName": "Aerial Traders"
                }
            },
            "companySummary": {
                "businessName": "Aerial Traders",
                "companyNumber": "SE00570381",
                "companyRegistrationNumber": "5560642554",
                "companyStatus": {
                    "description": "Active",
                    "status": "Active"
                },
                "country": country_alpha_2,
                "creditRating": {
                    "commonDescription": "Not Rated",
                    "commonValue": "E",
                    "creditLimit": {
                        "value": "0"
                    },
                    "providerDescription": "No account",
                    "providerValue": {
                        "value": "No credit rating"
                    }
                },
                "latestShareholdersEquityFigure": {
                    "value": 875000000.0
                },
                "latestTurnoverFigure": {
                    "value": 18752000000.0
                }
            },
            "contactInformation": {
                "mainAddress": {
                    "city": "ÄLMHULT",
                    "country": country_alpha_2,
                    "postalCode": "343 81",
                    "province": "KRONOBERG",
                    "simpleValue": "Box 700, 343 81 ÄLMHULT, KRONOBERG",
                    "street": "Box 700"
                }
            },
            "creditScore": {
                "currentContractLimit": {
                    "value": 46962500000.0
                },
                "currentCreditRating": {
                    "commonDescription": "Not Rated",
                    "commonValue": "E",
                    "creditLimit": {
                        "value": "0"
                    },
                    "providerDescription": "No account",
                    "providerValue": {
                        "value": "No credit rating"
                    }
                },
                "latestRatingChangeDate": "2019-11-01T00:00:00Z",
                "previousCreditRating": {
                    "commonDescription": "Not Rated",
                    "commonValue": "E",
                    "creditLimit": {
                        "value": "0"
                    },
                    "providerValue": {}
                }
            },
            "directors": {
                "currentDirectors": [
                    {
                        "dateOfBirth": "1950-01-06T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Male",
                        "name": "Anders Thure Christer Johnsson",
                        "positions": [
                            {
                                "dateAppointed": "2007-01-18T00:00:00Z",
                                "positionName": "Chairman of Board"
                            },
                            {
                                "dateAppointed": "2000-12-18T00:00:00Z",
                                "positionName": "Actual Member of Board"
                            }
                        ]
                    },
                    {
                        "dateOfBirth": "1955-09-15T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Male",
                        "name": "Thomas Gustav Carlzon",
                        "positions": [
                            {
                                "dateAppointed": "2007-01-18T00:00:00Z",
                                "positionName": "Actual Member of Board"
                            },
                            {
                                "dateAppointed": "2007-01-18T00:00:00Z",
                                "positionName": "Managing Director"
                            }
                        ]
                    },
                    {
                        "dateOfBirth": "1956-08-27T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Male",
                        "name": "Anders Gunnar Micael Gårlin",
                        "positions": [
                            {
                                "dateAppointed": "2008-05-13T00:00:00Z",
                                "positionName": "Actual Member of Board"
                            }
                        ]
                    },
                    {
                        "dateOfBirth": "1956-01-10T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Female",
                        "name": "Ann Margareta Johansson",
                        "positions": [
                            {
                                "dateAppointed": "2002-09-11T00:00:00Z",
                                "positionName": "Actual Member of Board"
                            },
                            {
                                "dateAppointed": "2000-05-10T00:00:00Z",
                                "positionName": "Employee Representative"
                            }
                        ]
                    },
                    {
                        "dateOfBirth": "1966-01-19T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Male",
                        "name": "Per Henrik Olshov",
                        "positions": [
                            {
                                "dateAppointed": "2001-12-11T00:00:00Z",
                                "positionName": "Actual Member of Board"
                            }
                        ]
                    },
                    {
                        "dateOfBirth": "1960-12-19T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Female",
                        "name": "Susanne Elisabet Håkansson",
                        "positions": [
                            {
                                "dateAppointed": "2009-03-27T00:00:00Z",
                                "positionName": "Actual Member of Board"
                            },
                            {
                                "dateAppointed": "2009-03-27T00:00:00Z",
                                "positionName": "Employee Representative"
                            }
                        ]
                    },
                    {
                        "dateOfBirth": "1966-03-21T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Male",
                        "name": "Bengt Thore Anders Kroon",
                        "positions": [
                            {
                                "dateAppointed": "2007-09-01T00:00:00Z",
                                "positionName": "Substitute"
                            },
                            {
                                "dateAppointed": "2007-09-01T00:00:00Z",
                                "positionName": "Employee Representative"
                            }
                        ]
                    },
                    {
                        "dateOfBirth": "1979-05-11T00:00:00Z",
                        "directorType": "Other",
                        "gender": "Male",
                        "name": "Johan Magnus Hagman",
                        "positions": [
                            {
                                "dateAppointed": "2008-07-29T00:00:00Z",
                                "positionName": "Substitute"
                            },
                            {
                                "dateAppointed": "2008-07-29T00:00:00Z",
                                "positionName": "Employee Representative"
                            }
                        ]
                    }
                ]
            },
            "financialStatements": [
                {
                    "balanceSheet": {
                        "bankLiabilities": 0.0,
                        "bankLiabilitiesDueAfter1Year": 0.0,
                        "calledUpShareCapital": 25000000.0,
                        "cash": 88000000.0,
                        "goodwill": 0.0,
                        "groupPayables": 503000000.0,
                        "groupPayablesDueAfter1Year": 0.0,
                        "groupReceivables": 103000000.0,
                        "landAndBuildings": 307000000.0,
                        "loansToGroup": 0.0,
                        "miscellaneousFixedAssets": 506000000.0,
                        "miscellaneousLiabilities": 3657000000.0,
                        "miscellaneousLiabilitiesDueAfter1Year": 873000000.0,
                        "miscellaneousReceivables": 3785000000.0,
                        "otherCurrentAssets": 286000000.0,
                        "otherIntangibleAssets": 0.0,
                        "otherInventories": 663000000.0,
                        "otherLoans": 0.0,
                        "otherLoansOrFinanceDueAfter1Year": 0.0,
                        "otherReserves": -382000000.0,
                        "otherTangibleAssets": 1108000000.0,
                        "plantAndMachinery": 0.0,
                        "revenueReserves": 1232000000.0,
                        "sharePremium": 0.0,
                        "totalAssets": 7457000000.0,
                        "totalCurrentAssets": 5536000000.0,
                        "totalCurrentLiabilities": 5709000000.0,
                        "totalFixedAssets": 1921000000.0,
                        "totalIntangibleAssets": 0.0,
                        "totalInventories": 663000000.0,
                        "totalLiabilities": 6582000000.0,
                        "totalLongTermLiabilities": 873000000.0,
                        "totalOtherFixedAssets": 506000000.0,
                        "totalReceivables": 4499000000.0,
                        "totalShareholdersEquity": 875000000.0,
                        "totalTangibleAssets": 1415000000.0,
                        "tradePayables": 1549000000.0,
                        "tradeReceivables": 611000000.0,
                        "workInProgress": 0.0
                    },
                    "consolidatedAccounts": False,
                    "currency": currency,
                    "numberOfWeeks": 52,
                    "otherFinancials": {
                        "contingentLiabilities": "45000000",
                        "netWorth": 875000000.0,
                        "workingCapital": -173000000.0
                    },
                    "profitAndLoss": {
                        "depreciation": 259000000.0,
                        "extraordinaryCosts": 0.0,
                        "extraordinaryIncome": 0.0,
                        "financialExpenses": 37000000.0,
                        "financialIncome": 41000000.0,
                        "minorityInterests": 0.0,
                        "operatingCosts": 17987000000.0,
                        "operatingProfit": 798000000.0,
                        "otherAppropriations": -1000000.0,
                        "profitAfterTax": 897000000.0,
                        "profitBeforeTax": 1110000000.0,
                        "retainedProfit": 896000000.0,
                        "revenue": 18785000000.0,
                        "tax": 213000000.0,
                        "wagesAndSalaries": 3100000000.0
                    },
                    "ratios": {
                        "creditorDays": 30.1,
                        "currentDebtRatio": 6.52,
                        "currentRatio": 0.97,
                        "debtorDays": 11.87,
                        "equityInPercentage": 11.73,
                        "gearing": 99.77,
                        "liquidityRatioOrAcidTest": 0.85,
                        "preTaxProfitMargin": 5.91,
                        "returnOnCapitalEmployed": 63.5,
                        "returnOnNetAssetsEmployed": 126.86,
                        "returnOnTotalAssetsEmployed": 14.89,
                        "salesOrNetWorkingCapital": -108.58,
                        "stockTurnoverRatio": 3.53,
                        "totalDebtRatio": 7.52
                    },
                    "type": "GlobalFinancialsGGS",
                    "yearEndDate": "2010-08-31T00:00:00Z"
                },
                {
                    "balanceSheet": {
                        "bankLiabilities": 60000000.0,
                        "bankLiabilitiesDueAfter1Year": 20000000.0,
                        "calledUpShareCapital": 25000000.0,
                        "cash": 96000000.0,
                        "goodwill": 0.0,
                        "groupPayables": 90000000.0,
                        "groupPayablesDueAfter1Year": 0.0,
                        "groupReceivables": 46000000.0,
                        "landAndBuildings": 385000000.0,
                        "loansToGroup": 0.0,
                        "miscellaneousFixedAssets": 293000000.0,
                        "miscellaneousLiabilities": 3741000000.0,
                        "miscellaneousLiabilitiesDueAfter1Year": 819000000.0,
                        "miscellaneousReceivables": 2999000000.0,
                        "otherCurrentAssets": 0.0,
                        "otherIntangibleAssets": 0.0,
                        "otherInventories": 555000000.0,
                        "otherLoans": 0.0,
                        "otherLoansOrFinanceDueAfter1Year": 0.0,
                        "otherReserves": 3929000.0,
                        "otherTangibleAssets": 766000000.0,
                        "plantAndMachinery": 0.0,
                        "revenueReserves": 236071000.0,
                        "sharePremium": 0.0,
                        "totalAssets": 6565000000.0,
                        "totalCurrentAssets": 5121000000.0,
                        "totalCurrentLiabilities": 5461000000.0,
                        "totalFixedAssets": 1444000000.0,
                        "totalIntangibleAssets": 0.0,
                        "totalInventories": 555000000.0,
                        "totalLiabilities": 6300000000.0,
                        "totalLongTermLiabilities": 839000000.0,
                        "totalOtherFixedAssets": 293000000.0,
                        "totalReceivables": 4470000000.0,
                        "totalShareholdersEquity": 265000000.0,
                        "totalTangibleAssets": 1151000000.0,
                        "tradePayables": 1570000000.0,
                        "tradeReceivables": 1425000000.0,
                        "workInProgress": 0.0
                    },
                    "consolidatedAccounts": False,
                    "currency": currency,
                    "numberOfWeeks": 52,
                    "otherFinancials": {
                        "contingentLiabilities": "46000000",
                        "netWorth": 265000000.0,
                        "workingCapital": -340000000.0
                    },
                    "profitAndLoss": {
                        "depreciation": 233000000.0,
                        "extraordinaryCosts": 0.0,
                        "extraordinaryIncome": 0.0,
                        "financialExpenses": 77000000.0,
                        "financialIncome": 95000000.0,
                        "minorityInterests": 0.0,
                        "operatingCosts": 25599000000.0,
                        "operatingProfit": 1038000000.0,
                        "otherAppropriations": -27000000.0,
                        "profitAfterTax": 712000000.0,
                        "profitBeforeTax": 1005000000.0,
                        "retainedProfit": 685000000.0,
                        "revenue": 26637000000.0,
                        "tax": 293000000.0,
                        "wagesAndSalaries": 2947000000.0
                    },
                    "ratios": {
                        "creditorDays": 21.51,
                        "currentDebtRatio": 20.61,
                        "currentRatio": 0.94,
                        "debtorDays": 19.53,
                        "equityInPercentage": 4.04,
                        "gearing": 339.25,
                        "liquidityRatioOrAcidTest": 0.84,
                        "preTaxProfitMargin": 3.77,
                        "returnOnCapitalEmployed": 91.03,
                        "returnOnNetAssetsEmployed": 379.25,
                        "returnOnTotalAssetsEmployed": 15.31,
                        "salesOrNetWorkingCapital": -78.34,
                        "stockTurnoverRatio": 2.08,
                        "totalDebtRatio": 23.77
                    },
                    "type": "GlobalFinancialsGGS",
                    "yearEndDate": "2009-08-31T00:00:00Z"
                },
                {
                    "balanceSheet": {
                        "bankLiabilities": 0.0,
                        "bankLiabilitiesDueAfter1Year": 0.0,
                        "calledUpShareCapital": 25000000.0,
                        "cash": 254000000.0,
                        "goodwill": 0.0,
                        "groupPayables": 90000000.0,
                        "groupPayablesDueAfter1Year": 0.0,
                        "groupReceivables": 118000000.0,
                        "landAndBuildings": 419000000.0,
                        "loansToGroup": 0.0,
                        "miscellaneousFixedAssets": 115000000.0,
                        "miscellaneousLiabilities": 2924000000.0,
                        "miscellaneousLiabilitiesDueAfter1Year": 766000000.0,
                        "miscellaneousReceivables": 3659000000.0,
                        "otherCurrentAssets": 179000000.0,
                        "otherIntangibleAssets": 0.0,
                        "otherInventories": 493000000.0,
                        "otherLoans": 0.0,
                        "otherLoansOrFinanceDueAfter1Year": 0.0,
                        "otherReserves": 5000000.0,
                        "otherTangibleAssets": 542000000.0,
                        "plantAndMachinery": 0.0,
                        "revenueReserves": 1621000000.0,
                        "sharePremium": 0.0,
                        "totalAssets": 7653000000.0,
                        "totalCurrentAssets": 6577000000.0,
                        "totalCurrentLiabilities": 5236000000.0,
                        "totalFixedAssets": 1076000000.0,
                        "totalIntangibleAssets": 0.0,
                        "totalInventories": 493000000.0,
                        "totalLiabilities": 6002000000.0,
                        "totalLongTermLiabilities": 766000000.0,
                        "totalOtherFixedAssets": 115000000.0,
                        "totalReceivables": 5651000000.0,
                        "totalShareholdersEquity": 1651000000.0,
                        "totalTangibleAssets": 961000000.0,
                        "tradePayables": 2222000000.0,
                        "tradeReceivables": 1874000000.0,
                        "workInProgress": 0.0
                    },
                    "consolidatedAccounts": False,
                    "currency": currency,
                    "numberOfWeeks": 52,
                    "otherFinancials": {
                        "contingentLiabilities": "36000000",
                        "netWorth": 1651000000.0,
                        "workingCapital": 1341000000.0
                    },
                    "profitAndLoss": {
                        "depreciation": 206000000.0,
                        "extraordinaryCosts": 0.0,
                        "extraordinaryIncome": 0.0,
                        "financialExpenses": 103000000.0,
                        "financialIncome": 161000000.0,
                        "minorityInterests": 0.0,
                        "operatingCosts": 25454000000.0,
                        "operatingProfit": 1919000000.0,
                        "otherAppropriations": -4000000.0,
                        "profitAfterTax": 1623000000.0,
                        "profitBeforeTax": 2176000000.0,
                        "retainedProfit": 1619000000.0,
                        "revenue": 27373000000.0,
                        "tax": 553000000.0,
                        "wagesAndSalaries": 2839000000.0
                    },
                    "ratios": {
                        "creditorDays": 29.63,
                        "currentDebtRatio": 3.17,
                        "currentRatio": 1.26,
                        "debtorDays": 24.99,
                        "equityInPercentage": 21.57,
                        "gearing": 46.4,
                        "liquidityRatioOrAcidTest": 1.16,
                        "preTaxProfitMargin": 7.95,
                        "returnOnCapitalEmployed": 90.03,
                        "returnOnNetAssetsEmployed": 131.8,
                        "returnOnTotalAssetsEmployed": 28.43,
                        "salesOrNetWorkingCapital": 20.41,
                        "stockTurnoverRatio": 1.8,
                        "totalDebtRatio": 3.64
                    },
                    "type": "GlobalFinancialsGGS",
                    "yearEndDate": "2008-08-31T00:00:00Z"
                },
                {
                    "balanceSheet": {
                        "bankLiabilities": 20000000.0,
                        "bankLiabilitiesDueAfter1Year": 0.0,
                        "calledUpShareCapital": 25000000.0,
                        "cash": 81000000.0,
                        "goodwill": 0.0,
                        "groupPayables": 119000000.0,
                        "groupPayablesDueAfter1Year": 0.0,
                        "groupReceivables": 110000000.0,
                        "landAndBuildings": 436000000.0,
                        "loansToGroup": 0.0,
                        "miscellaneousFixedAssets": 11000000.0,
                        "miscellaneousLiabilities": 2512000000.0,
                        "miscellaneousLiabilitiesDueAfter1Year": 733000000.0,
                        "miscellaneousReceivables": 3530000000.0,
                        "otherCurrentAssets": 148000000.0,
                        "otherIntangibleAssets": 0.0,
                        "otherInventories": 512000000.0,
                        "otherLoans": 0.0,
                        "otherLoansOrFinanceDueAfter1Year": 0.0,
                        "otherReserves": 4000000.0,
                        "otherTangibleAssets": 475000000.0,
                        "plantAndMachinery": 0.0,
                        "revenueReserves": 1677000000.0,
                        "sharePremium": 0.0,
                        "totalAssets": 7172000000.0,
                        "totalCurrentAssets": 6250000000.0,
                        "totalCurrentLiabilities": 4733000000.0,
                        "totalFixedAssets": 922000000.0,
                        "totalIntangibleAssets": 0.0,
                        "totalInventories": 512000000.0,
                        "totalLiabilities": 5466000000.0,
                        "totalLongTermLiabilities": 733000000.0,
                        "totalOtherFixedAssets": 11000000.0,
                        "totalReceivables": 5509000000.0,
                        "totalShareholdersEquity": 1706000000.0,
                        "totalTangibleAssets": 911000000.0,
                        "tradePayables": 2082000000.0,
                        "tradeReceivables": 1869000000.0,
                        "workInProgress": 0.0
                    },
                    "consolidatedAccounts": False,
                    "currency": currency,
                    "numberOfWeeks": 52,
                    "otherFinancials": {
                        "contingentLiabilities": "32000000",
                        "netWorth": 1706000000.0,
                        "workingCapital": 1517000000.0
                    },
                    "profitAndLoss": {
                        "depreciation": 216000000.0,
                        "extraordinaryCosts": 0.0,
                        "extraordinaryIncome": 0.0,
                        "financialExpenses": 95000000.0,
                        "financialIncome": 74000000.0,
                        "minorityInterests": 0.0,
                        "operatingCosts": 27343000000.0,
                        "operatingProfit": 2133000000.0,
                        "otherAppropriations": 17000000.0,
                        "profitAfterTax": 1631000000.0,
                        "profitBeforeTax": 2233000000.0,
                        "retainedProfit": 1648000000.0,
                        "revenue": 29476000000.0,
                        "tax": 602000000.0,
                        "wagesAndSalaries": 2680000000.0
                    },
                    "ratios": {
                        "creditorDays": 25.78,
                        "currentDebtRatio": 2.77,
                        "currentRatio": 1.32,
                        "debtorDays": 23.14,
                        "equityInPercentage": 23.79,
                        "gearing": 44.14,
                        "liquidityRatioOrAcidTest": 1.21,
                        "preTaxProfitMargin": 7.58,
                        "returnOnCapitalEmployed": 91.55,
                        "returnOnNetAssetsEmployed": 130.89,
                        "returnOnTotalAssetsEmployed": 31.13,
                        "salesOrNetWorkingCapital": 19.43,
                        "stockTurnoverRatio": 1.74,
                        "totalDebtRatio": 3.2
                    },
                    "type": "GlobalFinancialsGGS",
                    "yearEndDate": "2007-08-31T00:00:00Z"
                },
                {
                    "balanceSheet": {
                        "bankLiabilities": 196000000.0,
                        "bankLiabilitiesDueAfter1Year": 20000000.0,
                        "calledUpShareCapital": 25000000.0,
                        "cash": 70000000.0,
                        "goodwill": 0.0,
                        "groupPayables": 92000000.0,
                        "groupPayablesDueAfter1Year": 0.0,
                        "groupReceivables": 183000000.0,
                        "landAndBuildings": 455000000.0,
                        "loansToGroup": 0.0,
                        "miscellaneousFixedAssets": 2326000000.0,
                        "miscellaneousLiabilities": 3554000000.0,
                        "miscellaneousLiabilitiesDueAfter1Year": 716000000.0,
                        "miscellaneousReceivables": 635000000.0,
                        "otherCurrentAssets": 0.0,
                        "otherIntangibleAssets": 0.0,
                        "otherInventories": 2067000000.0,
                        "otherLoans": 0.0,
                        "otherLoansOrFinanceDueAfter1Year": 0.0,
                        "otherReserves": 5000000.0,
                        "otherTangibleAssets": 457000000.0,
                        "plantAndMachinery": 0.0,
                        "revenueReserves": 1508000000.0,
                        "sharePremium": 0.0,
                        "totalAssets": 7457000000.0,
                        "totalCurrentAssets": 4219000000.0,
                        "totalCurrentLiabilities": 5183000000.0,
                        "totalFixedAssets": 3238000000.0,
                        "totalIntangibleAssets": 0.0,
                        "totalInventories": 2067000000.0,
                        "totalLiabilities": 5919000000.0,
                        "totalLongTermLiabilities": 736000000.0,
                        "totalOtherFixedAssets": 2326000000.0,
                        "totalReceivables": 2082000000.0,
                        "totalShareholdersEquity": 1538000000.0,
                        "totalTangibleAssets": 912000000.0,
                        "tradePayables": 1341000000.0,
                        "tradeReceivables": 1264000000.0,
                        "workInProgress": 0.0
                    },
                    "consolidatedAccounts": False,
                    "currency": currency,
                    "numberOfWeeks": 52,
                    "otherFinancials": {
                        "contingentLiabilities": "29000000",
                        "netWorth": 1538000000.0,
                        "workingCapital": -964000000.0
                    },
                    "profitAndLoss": {
                        "depreciation": 226000000.0,
                        "extraordinaryCosts": 0.0,
                        "extraordinaryIncome": 0.0,
                        "financialExpenses": 92000000.0,
                        "financialIncome": 26000000.0,
                        "minorityInterests": 0.0,
                        "operatingCosts": 24036000000.0,
                        "operatingProfit": 2236000000.0,
                        "otherAppropriations": -6000000.0,
                        "profitAfterTax": 828000000.0,
                        "profitBeforeTax": 1434000000.0,
                        "retainedProfit": 822000000.0,
                        "revenue": 26272000000.0,
                        "tax": 606000000.0,
                        "wagesAndSalaries": 2336000000.0
                    },
                    "ratios": {
                        "creditorDays": 18.63,
                        "currentDebtRatio": 3.37,
                        "currentRatio": 0.81,
                        "debtorDays": 17.56,
                        "equityInPercentage": 20.62,
                        "gearing": 60.6,
                        "liquidityRatioOrAcidTest": 0.42,
                        "preTaxProfitMargin": 5.46,
                        "returnOnCapitalEmployed": 63.06,
                        "returnOnNetAssetsEmployed": 93.24,
                        "returnOnTotalAssetsEmployed": 19.23,
                        "salesOrNetWorkingCapital": -27.25,
                        "stockTurnoverRatio": 7.87,
                        "totalDebtRatio": 3.85
                    },
                    "type": "GlobalFinancialsGGS",
                    "yearEndDate": "2006-08-31T00:00:00Z"
                }
            ],
            "language": "EN",
            "negativeInformation": {
                "debtBalance": {
                    "balanceOfPrivateClaims": 0.0,
                    "balanceOfPublicClaims": 0.0,
                    "currency": currency,
                    "numberOfPrivateClaims": 0,
                    "numberOfPublicClaims": 0,
                    "totalBalance": 0.0
                },
                "recordOfNonPayment": {
                    "numberOfApplications": 0,
                    "numberOfDistraintOrRepossessions": 0,
                    "numberOfPrivateClaims": 0,
                    "numberOfPublicClaims": 0,
                    "numberOfRevokedApplications": 0
                }
            },
            "otherInformation": {
                "advisors": [
                    {
                        "auditorName": "Ernst & Young Aktiebolag"
                    }
                ],
                "employeesInformation": [
                    {
                        "numberOfEmployees": "5229",
                        "year": 2010
                    },
                    {
                        "numberOfEmployees": "5331",
                        "year": 2009
                    },
                    {
                        "numberOfEmployees": "5636",
                        "year": 2008
                    },
                    {
                        "numberOfEmployees": "5512",
                        "year": 2007
                    },
                    {
                        "numberOfEmployees": "4680",
                        "year": 2006
                    }
                ]
            },
            "shareCapitalStructure": {
                "issuedShareCapital": {
                    "value": 25000000.0
                }
            }
        },
        "userId": "101468838"
    }
