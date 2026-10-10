"""Confronta formulas candidatas com taxas publicadas; nao exporta dados por curso."""
import json
from collections import defaultdict
from pathlib import Path
import openpyxl

wb=openpyxl.load_workbook('data/raw/trajetoria2015.xlsx',read_only=True,data_only=True)
it=wb['INDICADORES_TRAJETORIA'].iter_rows(min_row=9,values_only=True)
h=list(next(it)); groups=defaultdict(list)
for row in it:
    d=dict(zip(h,row))
    if d.get('CO_UF')==51: groups[d['CO_CURSO']].append(d)
wb.close()
errors={name:[] for name in ['saldo','TAP','TCA','TDA','TCAN','TADA']}
for rows in groups.values():
    death=completion=dropout=0
    for d in sorted(rows,key=lambda x:x['NU_ANO_REFERENCIA']):
        death+=d['QT_FALECIDO'];completion+=d['QT_CONCLUINTE'];dropout+=d['QT_DESISTENCIA']
        denominator=d['QT_INGRESSANTE']-death
        errors['saldo'].append(abs(d['QT_INGRESSANTE']-(d['QT_PERMANENCIA']+completion+dropout+death)))
        if denominator<=0:continue
        for field,numerator in [('TAP',d['QT_PERMANENCIA']),('TCA',completion),('TDA',dropout),
                                ('TCAN',d['QT_CONCLUINTE']),('TADA',d['QT_DESISTENCIA'])]:
            errors[field].append(abs(100*numerator/denominator-d[field]))
out={
    'scope':'515 cursos MT da coorte 2015; 2015-2024',
    'candidate_denominator':'QT_INGRESSANTE menos soma acumulada de QT_FALECIDO',
    'candidate_numerators':'TCA/TDA usam soma acumulada; TAP/TCAN/TADA usam quantidade da referencia',
    'results':{k:{'tested':len(v),'max_absolute_error':max(v),'within_0_01':sum(x<=0.01 for x in v)} for k,v in errors.items()},
    'limitation':'Reconcilia este arquivo; nao substitui nota metodologica nem valida outras coortes.'
}
Path('outputs/fase1/reconciliacao_trajetoria.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
