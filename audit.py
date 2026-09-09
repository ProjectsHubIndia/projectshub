with open('templates/core/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'project_detail' in line or 'project.id' in line:
        print(f'{i-5} to {i+5}:')
        for j in range(max(0, i-5), min(len(lines), i+6)):
            print(f'{j+1}: {lines[j]}', end='')




