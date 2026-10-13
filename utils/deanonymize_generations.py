import re
import time
from pathlib import Path

import pandas as pd

from truthsplit_structured_knowledge_layer.profile_loader import ProfileLoader

path_current_file = Path(__file__).absolute()
profile_loader = ProfileLoader(
    path_current_file.parent.parent / 'truthsplit_structured_knowledge_layer' / 'profiles' / 'json'
)
profiles = profile_loader.profiles

models = [
    'anthropic/claude-sonnet-4.6',
    'openai/gpt-5.6-terra-pro',
    'google/gemma-4-31b-it',
    'x-ai/grok-4.5'
]
out = []
for model in models:
    for profile in profiles.keys():
        time_start = time.time()
        path_out = path_current_file.parent.parent / 'generations_anonymized' / profile / model.replace('/', '__')
        path_timing = path_out / 'timing.json'
        profile_generations = path_out.glob('*.txt')
        for pg in profile_generations:
            if 'global' in pg.name or 'local' in pg.name or 'emotional_appeal' in pg.name or 'overall_quality' in pg.name:
                topic, dimension1, dimension2, _id = pg.name.rsplit('_', maxsplit=3)
                dimension = f'{dimension1}_{dimension2}'
            else:
                topic, dimension, _id = pg.name.rsplit('_', maxsplit=2)
            _id = _id.split('.txt', maxsplit=1)[0]
            with open(pg, 'r', encoding='utf-8') as f:
                text = f.read()
            _, response = text.split('\n\n', maxsplit=1)
            corpus_text = response.split('How would you')[0].strip()
            path_original = path_current_file.parent.parent / 'dagstuhl-15512-argquality-corpus-v2' / 'dagstuhl-15512-argquality-corpus-unannotated' / f'{topic}.csv'

            df_original = pd.read_csv(path_original, sep="\t", encoding="iso-8859-1")

            text_original = df_original[df_original['#id'] == _id]['argument'].values[0]

            text_deanonymized = text.replace(corpus_text, text_original)
            path_deanonymized = path_current_file.parent.parent / 'generations_deanonymized' / profile / model.replace('/', '__') / f'{topic}_{dimension}_{_id}.txt'
            path_deanonymized.parent.mkdir(parents=True, exist_ok=True)
            with open(path_deanonymized, 'w', encoding='utf-8') as f:
                f.write(text_deanonymized)