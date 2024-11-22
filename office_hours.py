from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


'''
Where <> is a variable and () is optional:
Query := (<Q>) (is) (<TITLE>) <PROF>('s) <PROP>(?) 

Q := what
   | where
   | when

PROP := oh
      | office hours
      | hours
      | office
      | room
      | room number
      | email

PROF := <first name>
      | <last name>
      | <full name>

TITLE := Dr(.)
       | Prof(.)
'''

#
# Scraping
# 
def table2arr(table_html): 
    tdata = []
    table_body = table_html.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        tdata.append(cols)
    return tdata

def get_oh_tbl(tables):
    for table in tables:
        t_arr = table2arr(table)
        if "Office Hours" in t_arr[0]:
            return t_arr
        
def scrape_data():
    selector = 'div > table'
    url = 'https://csc.calpoly.edu/faculty/'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html_page = urlopen(req).read()

    soup = BeautifulSoup(html_page, 'html.parser')

    # Find the table using the specified CSS selector
    tables = soup.select(selector)

    oh_tbl = get_oh_tbl(tables)
    keys, values = oh_tbl[0], oh_tbl[1:]
    return values

#
# Parsing
# 

NAME_IDX = 0
OFFICE_IDX = 1
EMAIL_IDX = 2
OH_IDX = 3
H2C_IDX = 4

Q = ["what", "where", "when"]
TITLES = ["prof", "dr"]

OH_PROP = ["oh", "office hours", "hours"]
RM_PROP = ["room", "room number", "office"]
EM_PROP = ["email"]
OH, RM, EM = 1, 2, 3
PROPS = {OH : OH_PROP, RM : RM_PROP, EM : EM_PROP}

def ends_with_prop_type(s):
    for prop_ty in PROPS:
        for prop in PROPS[prop_ty]:
            if s.endswith(prop):
                return prop_ty
    return None

def remove_prop(s, prop_ty):
    for prop in PROPS[prop_ty]:
        if s.endswith(prop):
            return s.removesuffix(prop).strip()
    return None

# returns (first, last)
# assume input is either "last, first" or "first last"
def full_name_tup(name):
    if "," in name:
        return (name.split(",")[1].strip(), name.split(",")[0])
    else:
        return (name.split(" ")[0], name.split(" ")[1])

# given the prof, return a row index, list of valid names or none
def get_row_from_prof(name, rows):
    candidates = []
    name = name.lower()
    for idx, row in enumerate(rows):
        fst, lst = full_name_tup(row[NAME_IDX])
        fst, lst = fst.lower(), lst.lower()
        if name == f"{fst} {lst}" or name == f"{lst}, {fst}" or name == f"{lst} {fst}":
            return idx
        if fst.lower() in name.lower() or lst.lower() in name.lower():
            candidates.append((idx, f"{fst} {lst}"))

    if len(candidates) == 1:
        return candidates[0][0]
    elif len(candidates) > 1:
        return list(map(lambda tup: tup[1].title(), candidates))
    else:
        return None
def strip_Q(s):
    for q in Q:
        if s.startswith(q):
            return s.removeprefix(q).strip()
    return s
def strip_is(s):
    if s.startswith("is"):
        return s.removeprefix("is").strip()
    return s
def strip_title(s):
    for t in TITLES:
        if s.startswith(t):
            return s.removeprefix(t).strip(" \t\n.")
    return s
def remove_possessive(s):
    return s.replace('\'s', '')
def remove_question(s):
    if s.endswith("?"):
        return s.removesuffix("?").strip()
    return s
# convert QUERY into <PROP> <PROF>
def remove_sugar(s):
    s = s.lower()
    return strip_title(strip_is(strip_Q(remove_possessive(remove_question(s)))))
        

#
# Run query
# 

FMT_ERR = "Please enter a query in the form `when/what/where is <name>'s hours/class/email?`"
BIG_ERR = "Internal error. Contact maintainer."
def run_query(q, rows):
    """
    call with the user's question `q` : str, and a list of rows from the internet.
    """
    desugared_q = remove_sugar(q)
    p_ty = ends_with_prop_type(desugared_q)
    if p_ty is None:
        return FMT_ERR
    
    prof_name = remove_prop(desugared_q, p_ty)
    row_idx = get_row_from_prof(prof_name, rows)
    if isinstance(row_idx, list):
        profs_str = "/".join(row_idx[:2])
        return f"Multiple professors named `{prof_name}` found. Please use a full name (e.g. {profs_str}/etc.)"
    if row_idx is None:
        return f"No professor named `{prof_name}` in the office hours list, please check your spelling or https://csc.calpoly.edu/faculty/."
    
    row = rows[row_idx]
    titled_prof = prof_name.title()
    if p_ty == RM:
        if row[OFFICE_IDX] != "":
            return f"{titled_prof} is in room {row[OFFICE_IDX]}"
        else:
            return f"{titled_prof} has no office listed in the office hours table."
    elif p_ty == OH:
        if row[OH_IDX] != "":
            return f"{titled_prof} has hours {row[OH_IDX]} {f"({row[H2C_IDX]}, {row[OFFICE_IDX]})"}"
        else:
            return f"{titled_prof} has no hours listed in the office hours table."
    elif p_ty == EM:
        if row[EMAIL_IDX] != "":
            return f"{titled_prof} can be reached at {row[EMAIL_IDX]}."
        else:
            return f"{titled_prof} has no email listed in the office hours table."
    else:
        return BIG_ERR

def query_oh(q):
    return run_query(q, scrape_data())

#
# Tests
# 

assert remove_sugar("What is John's oh") == "john oh"
assert remove_sugar("where is Fooad's room?") == "fooad room"
assert remove_sugar("when bellardo Hours?") == "bellardo hours"
assert remove_sugar("Mike Email") == "mike email"

assert ends_with_prop_type("john oh") == OH
assert ends_with_prop_type("john hours") == OH
assert ends_with_prop_type("fooad room") == RM
assert ends_with_prop_type("fooad house") == None
assert ends_with_prop_type("clements email") == EM

values = scrape_data()
assert "Multiple professors" in run_query("what is John's office hours", values)
assert "14-204" in run_query("where is Dr. Khosmood's oh", values)
assert "jventu09@calpoly.edu" in run_query("ventura email?", values)


