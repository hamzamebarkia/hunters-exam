import json
import random

def generate_applicants(num_applicants=406):
    applicants = []
    types = ['normal'] * 360 + ['wildcard'] * 26 + ['ringer'] * 20
    random.shuffle(types)
    
    for i in range(num_applicants):
        app_type = types[i]
        
        # Base stats between 1 and 100
        stats = {
            'Speed': random.randint(10, 100),
            'Strength': random.randint(10, 100),
            'Intelligence': random.randint(10, 100),
            'Nen Control': random.randint(0, 50), # mostly low for applicants
            'Teamwork': random.randint(10, 100)
        }
        
        # Ringers have falsified high public stats but actually lower true stats
        true_stats = stats.copy()
        if app_type == 'ringer':
            stats = {k: min(100, v + random.randint(20, 50)) for k, v in true_stats.items()}
            
        applicant = {
            'id': f'A{i+1:03d}',
            'public_stats': stats,
            'true_stats': true_stats, # Hidden, only used for actual performance
            'energy': random.randint(300, 500),
            'type': app_type,
            'true_trust_scores': {} # populated later
        }
        applicants.append(applicant)
        
    # Populate true trust scores (-1.0 to 1.0)
    for i in range(num_applicants):
        for j in range(i+1, num_applicants):
            trust = random.uniform(-1.0, 1.0)
            applicants[i]['true_trust_scores'][applicants[j]['id']] = trust
            applicants[j]['true_trust_scores'][applicants[i]['id']] = trust
            
    return applicants

def generate_phases(num_phases=7):
    phases = []
    for i in range(num_phases):
        weights = {
            'Speed': random.random(),
            'Strength': random.random(),
            'Intelligence': random.random(),
            'Nen Control': random.random() * 0.5,
            'Teamwork': random.random()
        }
        # Normalize weights
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        phase = {
            'phase_id': f'P{i+1}',
            'stat_requirements': weights,
            'elimination_rate': random.uniform(0.1, 0.4), # 10% to 40% eliminated each phase
            'energy_cost': random.randint(30, 80),
            'alliance_multiplier': random.choice([0.5, 0.8, 1.0, 1.2, 1.5])
        }
        phases.append(phase)
    return phases

if __name__ == '__main__':
    applicants = generate_applicants()
    phases = generate_phases()
    
    with open('applicants.json', 'w') as f:
        json.dump(applicants, f, indent=2)
        
    with open('phases.json', 'w') as f:
        json.dump(phases, f, indent=2)
        
    print("Generated applicants.json and phases.json")
