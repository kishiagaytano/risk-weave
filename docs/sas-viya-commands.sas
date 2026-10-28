/* Risk Weave - SAS commands run so far in SAS Viya for Learners (SAS Studio).
   Read-only exploration of the full VFL tables; no table was created, saved
   or modified in CAS. Temporary WORK copies live only in the SAS session.
   Run order matches docs/sas-viya-observations.md. */

/* 0. Navigation (point and click): apps menu > Manage Data >
      Sources > In-memory data; filter "ilink" shows the CREDITr tables. */

/* 1. Session + caslib librefs.
      A first PROC CONTENTS failed with "Libref CREDITR is not assigned" until
      the caslibs were assigned. */
cas mysess;
caslib _all_ assign;

/* 2. Training table column list (83 columns). */
proc contents data=CREDITr.ILINK_CREDITRISK_TRAINING varnum; run;

/* 3. Table inventory (full scoring table name ends in _PUBLIC).
      A first attempt used CREDITr.ILINK_CREDITRISK_SCORING and failed. */
proc sql;
  select memname, nobs, nvar from dictionary.tables where libname='CREDITR';
quit;

/* 4. Target balance and numeric profile of the training table. */
proc freq data=CREDITr.ILINK_CREDITRISK_TRAINING; tables DEFAULT; run;
proc means data=CREDITr.ILINK_CREDITRISK_TRAINING n nmiss mean min max maxdec=2; run;

/* 5. Scoring table profile of key numeric fields. */
proc means data=CREDITr.ILINK_CREDITRISK_SCORING_PUBLIC n nmiss mean min max maxdec=2;
  var LOAN_ID LOAN_AMOUNT INTEREST_RATE LOAN_TERM MONTHLY_PAYMENT HOUSEHOLD_INCOME
      SAVINGS_BALANCE CHECKING_BALANCE FINANCIAL_LITERACY_SCORE HISTORIC_ACCESS_SCORE
      WEALTH_GAP_PROXY MEDICAL_DEBT_FLAG BRANCH_DISTANCE;
run;

/* 6. Category levels of selected character columns (training). */
proc freq data=CREDITr.ILINK_CREDITRISK_TRAINING nlevels;
  tables AGE_BAND GENDER RACE_ETH STATE_TIER RURAL_URBAN EDUCATION MARITAL_STATUS
         EMPLOYMENT_STATUS HOMEOWNER VEHICLE_TYPE NEW_USED_FLAG PREVIOUS_DENIAL_FLAG
         DEALER_NETWORK_TIER / missing;
run;

/* 7. Missing counts re-check (training). */
proc means data=CREDITr.ILINK_CREDITRISK_TRAINING nmiss maxdec=0;
  var HISTORIC_ACCESS_SCORE WEALTH_GAP_PROXY COST_OF_LIVING_INDEX MEDICAL_DEBT_FLAG
      BANKING_RELATIONSHIP_YRS FINANCIAL_PRODUCT_COUNT BRANCH_DISTANCE DEFAULT
      HOUSEHOLD_INCOME SAVINGS_BALANCE CHECKING_BALANCE FINANCIAL_LITERACY_SCORE;
run;

/* 8. DEFAULT rate by segment, by missing flag and by decile.
      Temporary WORK copies only. */
data work.t;
  set CREDITr.ILINK_CREDITRISK_TRAINING(keep=DEFAULT AGE_BAND GENDER RACE_ETH
      STATE_TIER RURAL_URBAN EDUCATION MARITAL_STATUS EMPLOYMENT_STATUS HOMEOWNER
      VEHICLE_TYPE NEW_USED_FLAG PREVIOUS_DENIAL_FLAG PREVIOUS_APPROVAL_FLAG
      SUBPRIME_HISTORY_FLAG DEALER_NETWORK_TIER HOUSEHOLD_INCOME SAVINGS_BALANCE
      CHECKING_BALANCE FINANCIAL_LITERACY_SCORE MEDICAL_DEBT_FLAG
      BANKING_RELATIONSHIP_YRS BRANCH_DISTANCE INTEREST_RATE DEBT_TO_INCOME
      LOAN_TO_VALUE);
  m_HH=missing(HOUSEHOLD_INCOME);          m_SAV=missing(SAVINGS_BALANCE);
  m_CHK=missing(CHECKING_BALANCE);         m_FLS=missing(FINANCIAL_LITERACY_SCORE);
  m_MED=missing(MEDICAL_DEBT_FLAG);        m_BNK=missing(BANKING_RELATIONSHIP_YRS);
  m_BRD=missing(BRANCH_DISTANCE);
run;

%macro seg(vars);
  %let i=1;
  %do %while(%scan(&vars,&i) ne );
    %let v=%scan(&vars,&i);
    proc means data=work.t n mean maxdec=4 nway; class &v / missing; var DEFAULT; run;
    %let i=%eval(&i+1);
  %end;
%mend;
%seg(AGE_BAND GENDER RACE_ETH STATE_TIER RURAL_URBAN EDUCATION MARITAL_STATUS
     EMPLOYMENT_STATUS HOMEOWNER VEHICLE_TYPE NEW_USED_FLAG PREVIOUS_DENIAL_FLAG
     PREVIOUS_APPROVAL_FLAG SUBPRIME_HISTORY_FLAG DEALER_NETWORK_TIER
     m_HH m_SAV m_CHK m_FLS m_MED m_BNK m_BRD);

proc rank data=work.t groups=10 out=work.r;
  var INTEREST_RATE DEBT_TO_INCOME LOAN_TO_VALUE;
  ranks r_ir r_dti r_ltv;
run;
proc means data=work.r n mean min max maxdec=4 nway; class r_ir;  var DEFAULT INTEREST_RATE;  run;
proc means data=work.r n mean min max maxdec=4 nway; class r_dti; var DEFAULT DEBT_TO_INCOME; run;
proc means data=work.r n mean min max maxdec=4 nway; class r_ltv; var DEFAULT LOAN_TO_VALUE;  run;
proc corr data=work.t spearman;
  var DEFAULT; with INTEREST_RATE DEBT_TO_INCOME LOAN_TO_VALUE;
run;
