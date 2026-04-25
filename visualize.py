import matplotlib.pyplot as plt
import re

def create_visualization(report_file):
    phases = []
    survivors = []
    
    # We start with 406 applicants
    survivors.append(406)
    phases.append("Start")
    
    with open(report_file, 'r') as f:
        content = f.read()
        
    phase_matches = re.finditer(r'Phase: (P\d+)', content)
    survivor_matches = list(re.finditer(r'Survivors Remaining: (\d+)', content))
    
    for p, s in zip(phase_matches, survivor_matches):
        phases.append(p.group(1))
        survivors.append(int(s.group(1)))
        
    plt.figure(figsize=(10, 6))
    plt.plot(phases, survivors, marker='o', linestyle='-', color='b', linewidth=2, markersize=8)
    
    plt.title('Hunter Exam Survival Curve', fontsize=16)
    plt.xlabel('Phase', fontsize=12)
    plt.ylabel('Number of Active Applicants', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add annotations
    for i, txt in enumerate(survivors):
        plt.annotate(txt, (phases[i], survivors[i]), textcoords="offset points", xytext=(0,10), ha='center')
        
    plt.tight_layout()
    plt.savefig('survival_visualization.png')
    print("Visualization saved as survival_visualization.png")

if __name__ == '__main__':
    create_visualization('Survival_Path_Report.txt')
