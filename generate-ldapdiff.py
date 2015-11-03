#!/usr/bin/python
__author__ = 'neon'
import sys
example_text =("committee_name=sexit\n"
                "ou=sexit\n"
                "display_name=sexIT\n"
                "start_gid_number=5076\n"
                "committee_type=Committee\n"
                "11\n"
                "mgustav\n"
                "warvik\n"
                "paulae\n"
                "gaband\n"
                "sjoanna\n"
                "oskarmo\n"
                "marhult\n"
                "10\n"
                "egero\n"
                "printz\n"
                "fionar\n"
                "jesande\n"
                "adamsc\n"
                "wdaniel\n"
                "09\n"
                "farnstra\n"
                "careng\n"
                "rydback\n"
                "lofw\n"
                "jstrom\n"
                "olape\n"
                "juliaad\n"
                "soderbem\n")

def make_diff_file(file_name,output_file_name):
    f = open(output_file_name,'w')

    ldap_diff = _generate_ldap_diff_from_file(file_name)
    f.write(ldap_diff)
    f.close()

def generate_example_input_file(file_name):
    f = open(file_name,'w')
    f.write(example_text)
    f.close()

def _generate_ldap_diff_from_file(file_name):
    f = open(file_name,'r')

    # The following calls have to be made in this order because of how the script
    # expects the input file to look
    committee_name = _get_committee(f)
    ou = _get_ou(f)
    display_name = _get_display_name(f)
    start_gid_number = _get_start_gid_number(f)
    committee_type = _get_committee_type(f)
    years_cid_map = _get_years_cid_map(f)

    f.close()

    complete_ldap_diff = generate_ldap_diff(years_cid_map,committee_name,display_name,ou,committee_type,start_gid_number)
    return complete_ldap_diff

def _get_years_cid_map(f):
    years_cid_map = {}
    cids = []
    year = -1

    for line in f:
        text = line.replace('\n', "")
        if _is_a_year(text):
            if year != -1:
                years_cid_map[year] = cids
                cids = []
            year = int(text)
        else:
            cids.append(text)

    years_cid_map[year] = cids
    return years_cid_map


def _get_committee_type(f):
    committee_type = f.readline()
    return committee_type.replace('\n', "").replace('committee_type=', "")

def _get_start_gid_number(f):
    start_gid_number = f.readline()
    return int(start_gid_number.replace('\n', "").replace('start_gid_number=', ""))

def _get_display_name(f):
    display_name = f.readline()
    return display_name.replace('\n', "").replace('display_name=', "")

def _get_ou(f):
    ou = f.readline()
    return ou.replace('\n', "").replace('ou=', "")

def _get_committee(f):
    committee_name = f.readline()
    return committee_name.replace('\n', "").replace('committee_name=', "")

##
# This function generates an ldap diff file for a specific committees earlier
# @param years_cids_map a dictionary containing the years as keys and a list of cids (strings) as value
# e.g. cids_each_year = {'10':["horv","harv","herv"],'09':["kek","neon","maxim"]}
# @param committee_name in lower case, as the node looks in ldap
# e.g. styrit, prit
# @param display_name how the name should look in the frontend
# e.g. digIT, P.R.I.T. snIT
# @param ou_node
# @param committee_type what type of association it is, a committee, union, board etc
# @start_gidnumber IMPORTANT, check what the next gidnumber is by trying to create a new child entry in ldap,
# then use that number, eg 5135
def generate_ldap_diff(year_cids_map, committee_name, display_name, ou_node,committee_type, start_gidnumber):
    gid_number = start_gidnumber
    ldap_diff = ""

    for year in year_cids_map:
        cids = year_cids_map[year]
        ldap_diff += _create_ldap_diff(year, cids, committee_name, display_name,committee_type, gid_number, ou_node)
        # increase the gid for next node
        gid_number += 1

    return ldap_diff

def _create_ldap_diff(year, cids, committee_name, display_name,committee_type, gid_number, ou_node):
    complete_ldap_diff = ""
    complete_ldap_diff += _create_committee_specific_part(committee_name, display_name, gid_number, ou_node, year)
    complete_ldap_diff += _create_all_members(cids)
    complete_ldap_diff += _create_closing_part(committee_type)
    complete_ldap_diff += '\n'
    return complete_ldap_diff

def _create_committee_specific_part(committee_name, display_name, gid_number, ou_node, year):
    ldap_diff = ("\n"
                  "dn: cn={committee_name}{year},ou={ou_node},ou=fkit,ou=groups,dc=chalmers,dc=it\n"
                  "changetype: add\n"
                  "cn: {committee_name}{year}\n"
                  "description: All members of {display_name} 20{year}\n"
                  "displayname: {display_name} 20{year}\n"
                  "gidnumber: {gid}")

    # Fill in the correct information
    year_string = _create_appropiate_string(year)
    ldap_diff = ldap_diff\
        .replace('{committee_name}', committee_name) \
        .replace('{year}', year_string) \
        .replace('{display_name}', display_name) \
        .replace('{ou_node}', ou_node) \
        .replace('{gid}', str(gid_number))
    return ldap_diff

def _create_appropiate_string(year):
    year_string = str(year)
    if (year < 10):
        year_string = "0" + year_string
    return year_string


def _create_all_members(cids):
    all_members = ""
    for cid in cids:
        all_members += "\nmember: uid=%s,ou=people,dc=chalmers,dc=it" % cid
    return all_members

def _create_closing_part(committee_type):
    return ("\n"
            "objectclass: posixGroup\n"
            "objectclass: groupOfNames\n"
            "objectclass: itGroup\n"
            "objectclass: top\n"
            "type: {committee_type}").replace('{committee_type}',committee_type)

def _is_a_year(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# Start of program
if len(sys.argv)==3:
    make_diff_file(sys.argv[1],sys.argv[2])
    print "ldapdif created as",sys.argv[2]
else:
    print "This is a script that can be used to generate diff files for ldap."
    generate_example_input_file("example_input_text_sexit.txt")
    print "Generated example_input_text_sexit.txt"
    print "Expecting two arguements, first the input file, second the output file"