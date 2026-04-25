import json
import random
import math

class HunterExamSimulation:
    def __init__(self, applicants_file, phases_file, my_id='A001'):
        with open(applicants_file, 'r') as f:
            self.all_applicants = json.load(f)
        with open(phases_file, 'r') as f:
            self.phases = json.load(f)
            
        self.active_applicants = {app['id']: app for app in self.all_applicants}
        self.my_id = my_id
        
        # Tracking variables
        self.estimated_trust = {app['id']: 0.0 for app in self.all_applicants if app['id'] != self.my_id}
        self.observed_performance = {app['id']: [] for app in self.all_applicants}
        self.flagged_ringers = set()
        self.flagged_wildcards = set()
        self.survival_log = []
        self.decisions_log = []
        
        self.my_stats = self.active_applicants[self.my_id]['public_stats']
        
    def calculate_base_performance(self, applicant, phase):
        stats = applicant['true_stats']
        weights = phase['stat_requirements']
        
        perf = sum(stats[stat] * weights[stat] for stat in weights)
        
        # Apply wildcard variance
        if applicant['type'] == 'wildcard':
            perf *= random.uniform(0.5, 1.5)
            
        return perf
        
    def detect_anomalies(self, phase_idx):
        for app_id, app in self.active_applicants.items():
            if app_id == self.my_id: continue
            
            perfs = self.observed_performance[app_id]
            if not perfs: continue
            
            # Predict expected performance based on public stats
            expected_perf_sum = 0
            for i, p in enumerate(self.phases[:phase_idx+1]):
                expected_perf_sum += sum(app['public_stats'][stat] * p['stat_requirements'][stat] for stat in p['stat_requirements'])
            
            avg_expected = expected_perf_sum / len(perfs)
            avg_actual = sum(perfs) / len(perfs)
            
            # Ringer detection
            if avg_actual < avg_expected * 0.7:
                self.flagged_ringers.add(app_id)
                
            # Wildcard detection
            if len(perfs) > 1:
                variance = sum((x - avg_actual)**2 for x in perfs) / len(perfs)
                if variance > 400: # high variance threshold
                    self.flagged_wildcards.add(app_id)

    def select_allies(self, phase):
        # Decide who to ally with based on estimated trust and phase requirements
        if phase['alliance_multiplier'] <= 1.0:
            return [] # Don't ally if it hinders or does nothing
            
        candidates = sorted(self.estimated_trust.keys(), key=lambda x: self.estimated_trust[x], reverse=True)
        # Select top 2 candidates if they are active
        allies = [c for c in candidates if c in self.active_applicants][:2]
        return allies
        
    def run_simulation(self):
        for phase_idx, phase in enumerate(self.phases):
            # 1. My Decision Phase
            # Estimate required performance. If high elimination rate or low energy, we must decide carefully.
            my_energy = self.active_applicants[self.my_id]['energy']
            elim_rate = phase['elimination_rate']
            
            # Should I exert or conserve?
            # If my energy is low (< 100), must conserve unless it's the final phase
            if my_energy < 150 and phase_idx < len(self.phases) - 1:
                strategy = 'conserve'
            elif elim_rate > 0.25:
                strategy = 'exert'
            else:
                strategy = 'conserve'
                
            allies = self.select_allies(phase)
            
            self.decisions_log.append({
                'phase': phase['phase_id'],
                'strategy': strategy,
                'allies': allies,
                'energy_before': my_energy
            })
            
            # 2. Performance Evaluation Phase
            phase_results = []
            
            for app_id, app in list(self.active_applicants.items()):
                perf = self.calculate_base_performance(app, phase)
                
                # Apply strategies and alliances for myself
                if app_id == self.my_id:
                    if strategy == 'exert':
                        perf *= 1.4
                        app['energy'] -= int(phase['energy_cost'] * 1.5)
                    else:
                        perf *= 0.8
                        app['energy'] -= int(phase['energy_cost'] * 0.5)
                        
                    # Apply alliances
                    if allies:
                        alliance_boost = 0
                        for ally_id in allies:
                            true_trust = app['true_trust_scores'][ally_id]
                            # Update estimated trust based on true trust + some noise
                            observed_trust = true_trust + random.uniform(-0.2, 0.2)
                            self.estimated_trust[ally_id] = self.estimated_trust[ally_id] * 0.5 + observed_trust * 0.5
                            
                            if true_trust > 0:
                                alliance_boost += true_trust * phase['alliance_multiplier']
                            else:
                                alliance_boost += true_trust # Penalty for bad trust
                        perf *= (1 + alliance_boost * 0.2)
                else:
                    # Others just use normal energy cost
                    app['energy'] -= phase['energy_cost']
                    
                # Store performance
                self.observed_performance[app_id].append(perf)
                phase_results.append((app_id, perf))
                
            # 3. Elimination Phase
            # Eliminate out of energy
            out_of_energy = [a for a in self.active_applicants.values() if a['energy'] <= 0]
            for a in out_of_energy:
                if a['id'] in self.active_applicants:
                    del self.active_applicants[a['id']]
                    
            # Eliminate bottom X percent
            num_to_eliminate = int(len(self.active_applicants) * phase['elimination_rate'])
            phase_results.sort(key=lambda x: x[1]) # Sort by performance ASC
            
            eliminated = 0
            for app_id, perf in phase_results:
                if eliminated >= num_to_eliminate:
                    break
                if app_id in self.active_applicants and app_id != self.my_id: # Assume I can fail too, wait:
                    del self.active_applicants[app_id]
                    eliminated += 1
                elif app_id == self.my_id:
                    # If I am in the bottom, do I fail? Let's say I fail.
                    self.survival_log.append(f"FAILED at {phase['phase_id']} due to low performance.")
                    return False
                    
            self.detect_anomalies(phase_idx)
            self.survival_log.append({
                'phase': phase['phase_id'],
                'survivors': len(self.active_applicants),
                'my_energy_after': self.active_applicants[self.my_id]['energy'] if self.my_id in self.active_applicants else 0
            })
            
            if self.my_id not in self.active_applicants:
                self.survival_log.append(f"FAILED at {phase['phase_id']} due to 0 energy.")
                return False
                
        self.survival_log.append("SURVIVED THE EXAM!")
        return True

    def generate_reports(self):
        # Survival Path Report
        with open('Survival_Path_Report.txt', 'w') as f:
            f.write("=== SURVIVAL PATH REPORT ===\n\n")
            f.write(f"Applicant ID: {self.my_id}\n\n")
            for i, dec in enumerate(self.decisions_log):
                f.write(f"Phase: {dec['phase']}\n")
                f.write(f"Energy Before: {dec['energy_before']}\n")
                f.write(f"Strategy: {dec['strategy'].upper()}\n")
                f.write(f"Allies Chosen: {', '.join(dec['allies']) if dec['allies'] else 'None'}\n")
                if i < len(self.survival_log) and isinstance(self.survival_log[i], dict):
                    f.write(f"Survivors Remaining: {self.survival_log[i]['survivors']}\n")
                    f.write(f"Energy After: {self.survival_log[i]['my_energy_after']}\n")
                f.write("-" * 30 + "\n")
            
            if isinstance(self.survival_log[-1], str):
                f.write(f"\nFinal Result: {self.survival_log[-1]}\n")
                
        # Strategy Document
        with open('Strategy_Document.txt', 'w') as f:
            f.write("=== HUNTER EXAM OPTIMIZATION STRATEGY ===\n\n")
            f.write("1. Modeling the Exam\n")
            f.write("The Exam is modeled as a sequence of phases. Each phase requires specific stat combinations.\n")
            f.write("Applicants have true stats (hidden) and public stats. Performance is a weighted sum of true stats based on phase requirements.\n")
            f.write("Energy is depleted each phase. Reaching 0 energy means elimination.\n\n")
            
            f.write("2. Optimization Algorithm\n")
            f.write("The strategy dynamically decides whether to 'exert' or 'conserve'.\n")
            f.write("If energy is dangerously low (<150), the algorithm defaults to conserve unless it's the final phase.\n")
            f.write("If the elimination rate of a phase is high (>25%), it opts to exert to ensure survival.\n\n")
            
            f.write("3. Handling Trust Uncertainty\n")
            f.write("Trust scores are hidden. The engine uses an 'estimated_trust' model that updates after an alliance is formed.\n")
            f.write("It adds a noise factor to simulate the uncertainty of human relationships. We only ally if the phase's alliance_multiplier > 1.0.\n\n")
            
            f.write("4. Detecting Wildcards and Ringers\n")
            f.write("The simulation tracks the observed performance of each applicant across phases.\n")
            f.write("Ringers: Detected if average actual performance is significantly lower (<70%) than expected performance based on public stats.\n")
            f.write(f"-> Detected Ringers: {', '.join(self.flagged_ringers) if self.flagged_ringers else 'None'}\n")
            f.write("Wildcards: Detected if the variance in their performance across phases exceeds a high threshold (400).\n")
            f.write(f"-> Detected Wildcards: {', '.join(self.flagged_wildcards) if self.flagged_wildcards else 'None'}\n\n")
            
            f.write("5. Edge Cases Accounted For\n")
            f.write("- Alliances failing due to hidden negative trust, which applies a penalty to performance.\n")
            f.write("- Running out of energy being an instant elimination criteria regardless of stat performance.\n")

if __name__ == '__main__':
    sim = HunterExamSimulation('applicants.json', 'phases.json')
    success = sim.run_simulation()
    sim.generate_reports()
    print("Simulation complete. Success:", success)
