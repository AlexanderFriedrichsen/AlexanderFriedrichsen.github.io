class MetagameAnalyzer:
    def __init__(self):
        self.decks = {}  # Will store deck names and meta shares
        self.matchups = {}  # Will store winrates against each deck
        
    def add_deck(self, name: str, meta_share: float):
        """Add a deck and its meta share percentage to the analysis."""
        self.decks[name] = meta_share/100  # Convert percentage to decimal
        
    def set_matchups(self, deck_name: str, winrates: dict):
        """Set winrates against each deck in the meta."""
        self.matchups = {deck: rate/100 for deck, rate in winrates.items()}  # Convert percentages to decimals
        
    def calculate_overall_winrate(self) -> float:
        """Calculate expected winrate against the field."""
        if not self.matchups:
            raise ValueError("No matchup data provided")
            
        total_winrate = 0
        for deck, meta_share in self.decks.items():
            if deck in self.matchups:
                winrate = self.matchups[deck]
                weighted_contribution = meta_share * winrate
                total_winrate += weighted_contribution
                
        return total_winrate * 100  # Convert back to percentage
    
    def validate_meta_shares(self) -> bool:
        """Check if meta shares sum to approximately 100%."""
        total = sum(self.decks.values())
        return abs(total - 1.0) < 0.001
    
    def get_matchup_details(self) -> list:
        """Get detailed breakdown of each matchup's contribution."""
        details = []
        for deck, meta_share in self.decks.items():
            if deck in self.matchups:
                winrate = self.matchups[deck]
                weighted_contribution = meta_share * winrate * 100
                details.append({
                    'deck': deck,
                    'meta_share': meta_share * 100,
                    'winrate': self.matchups[deck] * 100,
                    'contribution': weighted_contribution
                })
        return details

    def get_meta_share(self, deck_name: str) -> float:
        """Get the meta share percentage for a specific deck."""
        return self.decks.get(deck_name, 0) * 100  


# Example usage
if __name__ == "__main__":
    # Create analyzer
    analyzer = MetagameAnalyzer()
    
    # Add decks and their meta shares
    meta = {
        "BG Mid": 16,
        "Mono W": 12,
        "mono R": 12,
        "Domain": 12,
        "UW Eye": 18,
        "B Mid": 14,
        "Other": 10,
        "Convoke": 6
    }
    
    for deck, share in meta.items():
        analyzer.add_deck(deck, share)
    
    # Example matchup data
    matchups = {
        "BG Mid": 53, #50% winrate against deck 1
        "Mono W": 60,
        "mono R": 55,
        "Domain": 40,
        "UW Eye": 50,
        "B Mid": 55,
        "Other": 55,
        "Convoke": 50
    }
    
    analyzer.set_matchups("Your Deck", matchups)
    
    # Validate meta shares
    if not analyzer.validate_meta_shares():
        print("Warning: Meta shares do not sum to 100%")
    
    # Calculate and display results
    print("\nDetailed Matchup Analysis:")
    print("-" * 70)
    print(f"{'Deck':<15} {'Meta Share':<12} {'Winrate':<12} {'Contribution':<12}")
    print("-" * 70)
    
    for detail in analyzer.get_matchup_details():
        print(f"{detail['deck']:<15} {detail['meta_share']:>8.1f}%  {detail['winrate']:>8.1f}%  {detail['contribution']:>8.2f}%")
    
    print("-" * 70)
    overall_wr = analyzer.calculate_overall_winrate()
    print(f"\nExpected Overall Winrate: {overall_wr:.2f}%")