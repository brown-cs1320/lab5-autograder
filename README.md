# lab5-autograder
Autograder for lab5

## Caution

**Need to run within Brown Network**

## Usage

usage: autograde.py [-h] -t {mongo,mysql} filepath

Autograde Student CS132 Database Lab

positional arguments:
  filepath              Path to student's script

optional arguments:
  -h, --help            show this help message and exit
  -t {mongo,mysql}, --type {mongo,mysql}
                        Specify whether student use Mongo database or MySQL
                        database
 
### Example

```
python3 autograder.py -t=mongo <filepath-to-database-script>
```

```
python3 autograder.py -t=mysql <filepath-to-database-script>
```
