from urllib.parse import unquote

def decode_nt_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                # Split the line into subject, predicate, object parts
                parts = line.strip().split(' ', 2)
                
                if len(parts) == 3:
                    # Decode each part
                    subject = unquote(parts[0].strip('<>'))
                    predicate = unquote(parts[1].strip('<>'))
                    # Remove the trailing dot and space from object
                    object_part = parts[2].strip(' .')
                    object_uri = unquote(object_part.strip('<>'))
                    
                    # Reconstruct the line in N-Triples format
                    decoded_line = f"<{subject}> <{predicate}> <{object_uri}> .\n"
                    f_out.write(decoded_line)

# Use the function
input_file = 'linked_output_encode.nt'
output_file = 'linked_output.nt'

decode_nt_file(input_file, output_file)