// LoanLens - Customers query (dimension table, one row per borrower)
// Paste into: Home > Transform data > New Source > Blank Query > Advanced Editor
// Rename the query to: Customers
// Needs the DataFolder parameter (see 00_DataFolder_parameter.m)

let
    // Import
    Source = Csv.Document(
        File.Contents(DataFolder & "customers_raw.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Text hygiene: trim spaces, empty text -> null
    TrimmedText = Table.TransformColumns(PromotedHeaders, {}, each if _ is text then Text.Trim(_) else _),
    BlanksToNull = Table.ReplaceValue(TrimmedText, "", null, Replacer.ReplaceValue, Table.ColumnNames(TrimmedText)),

    // Remove duplicate rows
    RemovedDuplicates = Table.Distinct(BlanksToNull),

    // Standardize categories
    EmploymentMap = [#"full-time" = "Full-time", #"part-time" = "Part-time", #"self-employed" = "Self-employed", unemployed = "Unemployed"],
    EducationMap = [bachelors = "Bachelor's", masters = "Master's", #"high school" = "High School", phd = "PhD"],
    MaritalMap = [married = "Married", single = "Single", divorced = "Divorced"],

    // Lower-cases the value, optionally reshapes the key, then looks it up; anything unmatched -> "Unknown"
    LookUp = (value as nullable text, map as record, optional keyFn as function) as text =>
        if value = null then "Unknown"
        else Record.FieldOrDefault(
            map,
            if keyFn = null then Text.Lower(value) else keyFn(Text.Lower(value)),
            "Unknown"
        ),
    ToYesNo = (value as nullable text) as text =>
        if value = null then "Unknown"
        else if List.Contains({"yes", "y", "true", "1"}, Text.Lower(value)) then "Yes"
        else if List.Contains({"no", "n", "false", "0"}, Text.Lower(value)) then "No"
        else "Unknown",

    StandardizedText = Table.TransformColumns(RemovedDuplicates, {
        {"EmploymentType", each LookUp(_, EmploymentMap, (k) => Text.Replace(k, " ", "-")), type text},
        {"Education", each LookUp(_, EducationMap, (k) => Text.Remove(k, "'")), type text},
        {"MaritalStatus", each LookUp(_, MaritalMap), type text},
        {"HasMortgage", ToYesNo, type text},
        {"HasDependents", ToYesNo, type text}
    }),

    // Data types
    ChangedTypes = Table.TransformColumnTypes(StandardizedText, {
        {"CustomerID", type text},
        {"Age", Int64.Type},
        {"Income", Int64.Type},
        {"CreditScore", Int64.Type},
        {"MonthsEmployed", Int64.Type},
        {"NumCreditLines", Int64.Type}
    }, "en-US"),

    // Impossible values -> null
    FixedOutliers = Table.TransformColumns(ChangedTypes, {
        {"Age", each if _ = null or _ < 18 or _ > 100 then null else _, Int64.Type},
        {"CreditScore", each if _ = null or _ < 300 or _ > 850 then null else _, Int64.Type}
    }),

    // Missing Income -> median income (and flag it)
    MedianIncome = Number.Round(List.Median(List.RemoveNulls(FixedOutliers[Income]))),
    FlaggedIncome = Table.AddColumn(FixedOutliers, "IncomeImputed", each [Income] = null, type logical),
    ImputedIncome = Table.ReplaceValue(FlaggedIncome, null, MedianIncome, Replacer.ReplaceValue, {"Income"}),

    // Final column order
    Result = Table.SelectColumns(ImputedIncome, {
        "CustomerID", "Age", "Income", "IncomeImputed", "CreditScore", "MonthsEmployed",
        "NumCreditLines", "Education", "EmploymentType", "MaritalStatus", "HasMortgage", "HasDependents"
    })
in
    Result
