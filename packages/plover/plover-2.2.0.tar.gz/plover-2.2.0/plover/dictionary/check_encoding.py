import argparse

args = parser.parse_args()
print args.accumulate(args.integers)

def main():
    dict_filename = sys.argv[-1]

if __name__ == "__main__":
    default_encoding = 'utf-8'
    desc = 'Validate the character encoding of a stenography dictionary.'
    encoding_help = 'the character encoding to validate against (default: %s)' \
                    % default_encoding
    dict_help = 'a JSON-formatted stenography dictionary file'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-e', '--encoding', 
                        default=default_encoding,
                        help=encoding_help)
    parser.add_argument('dictionary_file', 
                        type=open, 
                        help=dict_help)

