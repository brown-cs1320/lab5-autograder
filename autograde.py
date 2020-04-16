import argparse
import itertools
import multiprocessing
import subprocess


def run_script(filepath, arguments, check_output, is_mongo, timeout=120):
    args = ['node', filepath]
    args.extend(arguments)
    try:
        process = subprocess.run(args, capture_output=True, timeout=timeout, check=True, text=True)
        return check_output(process.stdout, is_mongo)
    except subprocess.TimeoutExpired as err:
        return f'{err.cmd} fails because of timeout after {err.timeout} seconds'
    except subprocess.CalledProcessError as err:
        return f'{err.cmd} fails because of an error in execution {err.stderr}'


def check_single_line_output(stdout, expected_output):
    stdout = stdout.strip()
    if stdout == expected_output:
        return f'[O] Expected: {expected_output} | Received {stdout}'
    else:
        return f'[X] Expected: {expected_output} | Received {stdout}'


sep = ', '


def check_set_equality(stdout, expected_output):
    stdout_set = set(stdout.splitlines())
    if stdout_set == expected_output:
        return f'[O] Expected: {sep.join(expected_output)} | Received {sep.join(stdout_set)}'
    else:
        return f'[X] Expected: {sep.join(expected_output)} | Received {sep.join(stdout_set)} | {sep.join(expected_output.difference(stdout_set))} is in expected output but not actual output | {sep.join(stdout_set.difference(expected_output))} is in actual output but not expected output '


def check_is_subset(stdout, expected_output):
    stdout_set = set(stdout.splitlines())
    if stdout_set.issubset(expected_output):
        return f'[O] {sep.join(stdout_set)} is subset of {sep.join(expected_output)}'
    else:
        return f'[X] {sep.join(stdout_set)} is not subset of {sep.join(expected_output)}: {sep.join(stdout_set.difference(expected_output))} does not belong to expected output'


def check_empty_output(stdout):
    if stdout.strip() == '':
        return f'[O] Expected: EMPTY OUTPUT | Received {stdout}'
    else:
        return f'[X] Expected: EMPTY OUTPUT | Received {stdout}'


expected_mongo_output_for_search = set(['Adam Melchor', 'David Bowie', 'Dezo Ursiny', 'Fairway', 'Forever The Sickest Kids', 'Johnny Cash', 'King Crimson', 'The Auteurs', 'Timber Timbre'])
expected_mysql_output_for_search = set(['PeterTG', 'Various Artists', 'The Tarney - Spencer Band', 'Alchem', 'Bidiniband', 'D-A-D', 'Furthur', 'Ventures The', 'The Takeover Uk', 'Vertical Horizon', 'Ianva', 'Eddie Vedder', 'Black Lips', 'Various', 'Placebo', 'Ingrid Michaelson', 'Morse Code', 'Gov T Mule', 'El Tri', 'Mangoo', 'I Am Kloot', 'The Hard Lesson', 'Dan Baird & Homemade Sin', 'Wolfmother', 'PLASTICZOOMS', 'Hybrid Ice', 'Bob Sinclar', 'Juraya', 'U2', 'Burn Hollywood Burn', 'Ray Davies The Crouch End Festival Chorus', 'The Backyards', 'Chickenfoot', 'Gluecifer', 'Kevin Devine', 'The Band', 'Survivor', 'Roger Taylor', 'Black Eyed Peas'])


def check_output_is_false(output, is_mongo):
    return check_single_line_output(output, 'false')


def check_output_is_true(output, is_mongo):
    return check_single_line_output(output, 'true')


def check_output_is_empty(output, is_mongo):
    return check_empty_output(output)


def check_output_set_equals(output, is_mongo):
    return check_set_equality(output, expected_mongo_output_for_search if is_mongo else expected_mysql_output_for_search)


def check_output_is_subset(output, is_mongo):
    return check_is_subset(output, expected_mongo_output_for_search if is_mongo else expected_mysql_output_for_search)

def search_correct_arguments(is_mongo):
    return ['search', 'The Beatles', '9' if is_mongo else '39']


checks = [
    {
        'title': 'related: both name not exist',
        'arguments': ['related', 'xxxx', 'xxxx'],
        'check_output': check_output_is_false
    },
    {
        'title': 'related: one name not exists',
        'arguments': ['related', 'xxxx', 'The Beatles'],
        'check_output': check_output_is_false
    },
    {
        'title': 'related: unrelated artists',
        'arguments': ['related', 'Pink Floyd', 'Lang Lang'],
        'check_output': check_output_is_false
    },
    {
        'title': 'related: related artists',
        'arguments': ['related', 'The Beatles', 'The Beach Boys'],
        'check_output': check_output_is_true
    },
    {
        'title': 'search: artist not exist',
        'arguments': ['search', 'xxxxx', '5'],
        'check_output': check_output_is_empty
    },
    {
        'title': 'search: correct output for artist',
        'arguments': search_correct_arguments,
        'check_output': check_output_set_equals
    },
    {
        'title': 'search: correct LIMIT for artist',
        'arguments': ['search', 'The Beatles', '5'],
        'check_output': check_output_is_subset
    },
]


print_lock = multiprocessing.Lock()


def run_check(filepath, is_mongo, check):
    arguments = check['arguments'] if isinstance(check['arguments'], list) else check['arguments'](is_mongo)
    result = run_script(filepath, arguments, check['check_output'], is_mongo)
    with print_lock:
        print(f'''
Running check: {check["title"]}
{result}
        ''')


def run_checks(filepath, is_mongo):
    #  for check in checks:
    #      run_check(filepath, is_mongo, check)
    with multiprocessing.Pool() as pool:
        pool.starmap(run_check, zip(itertools.repeat(filepath), itertools.repeat(is_mongo), checks))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Autograde Student CS132 Database Lab")
    parser.add_argument(
        '-t', '--type', choices=["mongo", 'mysql'], required=True,
        help="Specify whether student use Mongo database or MySQL database")
    parser.add_argument('filepath', help="Path to student's script")
    args = parser.parse_args()
    is_mongo = args.type == "mongo"
    run_checks(args.filepath, is_mongo)
