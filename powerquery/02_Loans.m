// LoanLens - Loans query (fact table, one row per loan)
// Paste into: Home > Transform data > New Source > Blank Query > Advanced Editor
// Rename the query to: Loans
// Needs the DataFolder parameter (see 00_DataFolder_parameter.m)

let
    // Import
    Source = Csv.Document(
        File.Contents(DataFolder & "loans_raw.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Text hygiene: trim spaces, empty text -> null
    TrimmedText = Table.TransformColumns(PromotedHeaders, {}, each if _ is text then Text.Trim(_) else _),
    BlanksToNull = Table.ReplaceValue(TrimmedText, "", null, Replacer.ReplaceValue, Table.ColumnNames(TrimmedText)),

    // Remove duplicate rows
    RemovedDuplicates = Table.Distinct(BlanksToNull),

    // Fix formats and standardize categories
    PurposeMap = [auto = "Auto", business = "Business", education = "Education", home = "Home", other = "Other"],
    ToYesNo = (value as nullable text) as text =>
        if value = null then "Unknown"
        else if List.Contains({"yes", "y", "true", "1"}, Text.Lower(value)) then "Yes"
        else if List.Contains({"no", "n", "false", "0"}, Text.Lower(value)) then "No"
        else "Unknown",
    ToDefaultFlag = (value as nullable text) as nullable number =>
        if value = null then null
        else if List.Contains({"1", "yes", "y", "true"}, Text.Lower(value)) then 1
        else if List.Contains({"0", "no", "n", "false"}, Text.Lower(value)) then 0
        else null,
    // Dates arrive as yyyy-MM-dd or dd/MM/yyyy
    ParseDate = (value as nullable text) as nullable date =>
        if value = null then null
        else try Date.FromText(value, [Format = "yyyy-MM-dd", Culture = "en-US"])
             otherwise try Date.FromText(value, [Format = "dd/MM/yyyy", Culture = "en-US"])
             otherwise null,

    CleanedText = Table.TransformColumns(RemovedDuplicates, {
        {"InterestRate", each if _ = null then null else Number.FromText(Text.Remove(_, "%"), "en-US"), type nullable number},
        {"LoanPurpose", each if _ = null then "Unknown" else Record.FieldOrDefault(PurposeMap, Text.Lower(_), "Unknown"), type text},
        {"HasCoSigner", ToYesNo, type text},
        {"Default", ToDefaultFlag, Int64.Type},
        {"IssueDate", ParseDate, type date}
    }),

    // Data types
    ChangedTypes = Table.TransformColumnTypes(CleanedText, {
        {"LoanID", type text},
        {"CustomerID", type text},
        {"LoanAmount", Int64.Type},
        {"LoanTerm", Int64.Type},
        {"DTIRatio", type number}
    }, "en-US"),

    // Impossible loan terms -> null
    FixedLoanTerm = Table.TransformColumns(ChangedTypes, {
        {"LoanTerm", each if List.Contains({12, 24, 36, 48, 60}, _) then _ else null, Int64.Type}
    }),

    // Missing InterestRate -> median rate (and flag it)
    MedianRate = List.Median(List.RemoveNulls(FixedLoanTerm[InterestRate])),
    FlaggedRate = Table.AddColumn(FixedLoanTerm, "InterestRateImputed", each [InterestRate] = null, type logical),
    ImputedRate = Table.ReplaceValue(FlaggedRate, null, MedianRate, Replacer.ReplaceValue, {"InterestRate"}),

    // Readable status column (used by the Default Rate measure)
    AddedStatus = Table.AddColumn(ImputedRate, "LoanStatus", each if [Default] = 1 then "Default" else "Non-Default", type text),

    // Final column order
    Result = Table.SelectColumns(AddedStatus, {
        "LoanID", "CustomerID", "IssueDate", "LoanAmount", "InterestRate", "InterestRateImputed",
        "LoanTerm", "DTIRatio", "LoanPurpose", "HasCoSigner", "Default", "LoanStatus"
    })
in
    Result
