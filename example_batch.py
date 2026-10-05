"""Пример: по дереву на каждого сотрудника (для визиток). python3 example_batch.py"""
import treelib as T
staff = [('Иванов', 417), ('Петрова', 1203), ('Асанов', 2981)]
for name, seed in staff:
    inner, (x0, y0, x1, y1) = T.build(T.preset('Пучок', seed=seed), '#17191E')
    pad = 40
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-pad} {y0-pad} {x1-x0+2*pad} {y1-y0+2*pad}">'
           f'<rect x="{x0-pad}" y="{y0-pad}" width="{x1-x0+2*pad}" height="{y1-y0+2*pad}" fill="#17191E"/>{inner}</svg>')
    open(f'tree-{seed:04d}.svg', 'w').write(svg)
    print('tree-%04d.svg' % seed, name)
