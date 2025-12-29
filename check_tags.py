
import re

filename = r'd:\British_school_UAE\blossom_school\templates\payments\student_payment_details.html'

with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines):
    # Find all tags
    tags = re.findall(r'{%\s*(\w+)', line)
    for tag in tags:
        if tag in ['if', 'for', 'block', 'with', 'while']:
            stack.append((tag, i + 1))
        elif tag in ['endif', 'endfor', 'endblock', 'endwith', 'endwhile']:
            if not stack:
                print(f"Error: Unexpected {{% {tag} %}} at line {i+1}")
            else:
                last_tag, last_line = stack[-1]
                expected_end = 'end' + last_tag
                if tag == expected_end:
                    stack.pop()
                else:
                    # Ignore mismatches if they are just nested loop/if logic that requires careful parsing
                     # But basic structure check:
                    if tag == 'endblock' and last_tag == 'if':
                         print(f"Error: Found {{% {tag} %}} at line {i+1} but expected {{% endif %}} for {{% if %}} at line {last_line}")
                    elif tag == 'endif' and last_tag != 'if':
                         pass # Allow loose nesting if regex is imperfect, but report interesting ones
                    
                    if tag == expected_end:
                         stack.pop()

if stack:
    print("Unclosed tags:")
    for tag, line in stack:
        print(f"{{% {tag} %}} at line {line}")
