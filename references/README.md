# Assessment reference

Save the original email attachment as `private/Default_report_format.pdf`, or set
`REPORT_REFERENCE_PATH` to its absolute path. The PDF is intentionally ignored by
Git because it contains the supplied report's patient details. It is the runtime
source for normal reference-format downloads. The exact default is returned
byte-for-byte. Reviewers must install their own authorized copy separately.

Do not commit the original PDF or derived clinical page images. Automated tests use
a generated nonclinical reference fixture and the portable synthetic renderer.
