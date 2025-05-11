#!/usr/bin/env python3
import time
import random
import sys

# === Configuration ===
NUM_HORSES    = 6
TRACK_LENGTH  = 50
MAX_STEP      = 1.5
TICK_DELAY    = 0.1
HORSE_SYMBOLS = ["🐎", "🏇", "🐴", "🐎", "🏇", "🐴"]
BET_TYPES     = ["Win", "Place", "Show", "Exacta"]


def clear_screen():
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


def render(positions, balance, odds):
    clear_screen()
    print("🐎  Horse Race Simulator 🏇")
    print(f"💰 Balance: $ {balance:,.2f}")
    print("=" * (TRACK_LENGTH + 30))
    print("📈 Odds: " + "  ".join([f"{i+1}:{odd:.2f}" for i, odd in enumerate(odds)]))
    print("=" * (TRACK_LENGTH + 30))

    for idx, pos in enumerate(positions):
        p = min(int(pos), TRACK_LENGTH)
        line = (
            f"Horse {idx+1:>2} {HORSE_SYMBOLS[idx]}: "
            + "·" * p
            + HORSE_SYMBOLS[idx]
            + " " * (TRACK_LENGTH - p)
            + "| FINISH"
        )
        print(line)
    print("=" * (TRACK_LENGTH + 30))


def get_bet_type(balance):
    print("\nAvailable bet types:")
    for i, bt in enumerate(BET_TYPES, 1):
        print(f"  {i}. {bt}")
    while True:
        sel = input(f"Choose bet type (1-{len(BET_TYPES)}), or 'q' to quit: ")
        if sel.lower() == 'q':
            print("Goodbye!"); sys.exit()
        if sel.isdigit() and 1 <= int(sel) <= len(BET_TYPES):
            return BET_TYPES[int(sel) - 1]
        print("❌ Invalid selection.")


def get_horse_selection(prompt, exclude=None):
    while True:
        pick = input(prompt)
        if pick.isdigit():
            idx = int(pick) - 1
            if 0 <= idx < NUM_HORSES and (exclude is None or idx != exclude):
                return idx
        print("❌ Invalid horse number.")


def get_stake(balance):
    while True:
        stake = input(f"Enter stake (up to $ {balance:,.2f}): $")
        try:
            stake = float(stake)
            if 0 < stake <= balance:
                return stake
        except:
            pass
        print("❌ Invalid stake.")


def race():
    positions = [0.0] * NUM_HORSES
    while True:
        for i in range(NUM_HORSES):
            positions[i] += random.uniform(0, MAX_STEP)
            if positions[i] >= TRACK_LENGTH:
                return positions
        render(positions, balance, fair_odds)
        time.sleep(TICK_DELAY)


def summarize_results(finishers):
    clear_screen()
    print("🎉  Race Results 🎉")
    for place, idx in enumerate(finishers, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(place, f"{place}.")
        print(f"  {medal} Horse {idx+1} {HORSE_SYMBOLS[idx]}")
    print()


# === Main Loop ===
balance = 1000.0

while True:
    clear_screen()
    print("🐎  Welcome to the Horse Race Simulator 🏇")
    print(f"💰 Current Balance: $ {balance:,.2f}\n")

    # Generate odds
    strengths = [random.uniform(1.0, 5.0) for _ in range(NUM_HORSES)]
    total_strength = sum(strengths)
    win_probs = [s / total_strength for s in strengths]
    fair_odds = [1 / p for p in win_probs]

    # Show odds
    print("Tonight's horses and odds:")
    for i, (odds, prob) in enumerate(zip(fair_odds, win_probs)):
        print(f"  Horse {i+1} {HORSE_SYMBOLS[i]} — {odds:.2f}:1 (Win Chance: {prob*100:.1f}%)")

    # Bet input
    bet_type = get_bet_type(balance)

    if bet_type == "Exacta":
        pick1 = get_horse_selection("Select WINNER horse (1–6): ")
        pick2 = get_horse_selection("Select RUNNER-UP horse (1–6): ", exclude=pick1)
        bet_data = (pick1, pick2)
    else:
        bet_data = get_horse_selection(f"Select Horse (1–{NUM_HORSES}) to {bet_type}: ")

    stake = get_stake(balance)
    print(f"\n📣 Betting $ {stake:,.2f} on {bet_type}...\n")
    time.sleep(1)

    # Run race
    positions = race()
    finishers = sorted(range(NUM_HORSES), key=lambda i: -positions[i])
    summarize_results(finishers)

    # Payout logic
    result, payout = "", 0
    if bet_type == "Win":
        if finishers[0] == bet_data:
            payout = stake * fair_odds[bet_data]
            result = "🏆 WIN! You nailed it!"
        else:
            result = "❌ Lose."
    elif bet_type == "Place":
        if bet_data in finishers[:2]:
            payout = stake * (1 / (win_probs[bet_data] * 2))
            result = "🏅 PLACE! Not bad!"
        else:
            result = "❌ No place."
    elif bet_type == "Show":
        if bet_data in finishers[:3]:
            payout = stake * (1 / (win_probs[bet_data] * 3))
            result = "🎖 SHOW! You placed top 3!"
        else:
            result = "❌ No show."
    elif bet_type == "Exacta":
        p1, p2 = bet_data
        if finishers[0] == p1 and finishers[1] == p2:
            payout = stake * (1 / (win_probs[p1] * win_probs[p2]))
            result = "🎯 EXACTA! Dead on!"
        else:
            result = "❌ Exacta missed."

    # Apply balance changes
    if payout > 0:
        balance += payout - stake
        print(f"{result} You win $ {payout:,.2f} (incl. stake).")
    else:
        balance -= stake
        print(f"{result} You lose $ {stake:,.2f}.")

    print(f"💵 New Balance: $ {balance:,.2f}\n")

    if balance <= 0:
        print("💀 Bankrupt. Game Over.")
        break

    if input("Play again? (y/n): ").lower() != 'y':
        print("👋 Thanks for playing!")
        break
