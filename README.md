# getVerificationTestList
This script can be used to extract the names of all the tests or sequences that are run
as part of a regression. The results are normally located in a separate directories. These directories could have
the following form:
    run<seed_number> or sim<seed_number> or test<seed_number> etc.

At the moment, this script assumes that the results of all the tests that were run during the regression are stored in
sim_<seed_number> directories. It is also assumed that these sim_<seed_number> directories are located in a directory that
ends in:
    .../designs/<design_name>/results

The script accepts the absolute path to the directory where all the result directories (sim_<seed_number>) are. An example of calling
the script might be:

    "get_test_list.py --path /home/dylanKB/projects/multiplier/results"

A list of all the tests is written to an output text file which has the following form:

    "<design_name>_test_list.txt"
    
An idea: You can add an alias to your ~/.aliases file that will point to the script - e.g.:

    "alias get_test_list '<path_to_directory_with_script>/get_test_list.py'"

Then, you can simply call 'get_test_list --path <absolute_path_to_directory_with_sim_dirs>' from *anywhere* in your
Linux environment (assumming you have sourced your .aliases file)