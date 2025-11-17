root ::= transaction_response
transaction_response ::= "{" "\"transactions_exist\"" ":" boolean "," "\"transactions\"" ":" transaction_list "}"
transaction_list ::= "[" (transaction ("," transaction)*)? "]"
transaction ::= "{" "\"summary\"" ":" string "}"
string ::= "\"" (
    [^\"\\\x00-\x1F] |
    "\\" (["\\bfnrt])
)* "\""
boolean ::= "true" | "false"
