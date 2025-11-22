#!/usr/bin/env python3
"""
NFT Storage Provider Selection Guide
Helps users choose between Pinata IPFS and Filecoin Cloud based on their needs
"""

import os
import sys
import time
from pathlib import Path


# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header():
    """Print selection guide header"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 70)
    print("🔗 NFT STORAGE PROVIDER SELECTION GUIDE")
    print("=" * 70)
    print(f"{Colors.END}")
    print(
        f"{Colors.WHITE}Choose the best storage solution for your NFT project{Colors.END}\n"
    )


def print_provider_comparison():
    """Display detailed comparison between providers"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}📊 PROVIDER COMPARISON{Colors.END}")
    print("=" * 50)
    print()

    # Pinata IPFS
    print(f"{Colors.GREEN}{Colors.BOLD}🍍 PINATA IPFS{Colors.END}")
    print(f"{Colors.GREEN}✅ RECOMMENDED FOR BEGINNERS{Colors.END}")
    print(f"   {Colors.CYAN}Setup Time:{Colors.END} 2-3 minutes")
    print(f"   {Colors.CYAN}Difficulty:{Colors.END} Easy ⭐")
    print(f"   {Colors.CYAN}Reliability:{Colors.END} Very High ⭐⭐⭐⭐⭐")
    print(f"   {Colors.CYAN}Speed:{Colors.END} Fast ⭐⭐⭐⭐")
    print()
    print("   📋 Pros:")
    print("   • Instant setup - no approval needed")
    print("   • Reliable service with 99.9% uptime")
    print("   • Great for prototypes and production")
    print("   • Excellent documentation and support")
    print("   • 1GB free storage included")
    print("   • Works immediately with your app")
    print()
    print("   📋 Cons:")
    print("   • Monthly subscription for more storage")
    print("   • Centralized service (though data is on IPFS)")
    print("   • Limited free tier")
    print()
    print(
        f"   {Colors.CYAN}Best for:{Colors.END} Most users, quick setup, production apps"
    )
    print(f"   {Colors.CYAN}Cost:{Colors.END} Free (1GB) → $20/month (100GB)")
    print()

    # Filecoin Cloud
    print(f"{Colors.BLUE}{Colors.BOLD}🌐 FILECOIN CLOUD{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  ADVANCED USERS ONLY{Colors.END}")
    print(f"   {Colors.CYAN}Setup Time:{Colors.END} 30-60 minutes")
    print(f"   {Colors.CYAN}Difficulty:{Colors.END} Very Hard ⭐⭐⭐⭐⭐")
    print(f"   {Colors.CYAN}Reliability:{Colors.END} Medium (Alpha) ⭐⭐⭐")
    print(f"   {Colors.CYAN}Speed:{Colors.END} Medium ⭐⭐⭐")
    print()
    print("   📋 Pros:")
    print("   • Truly decentralized storage")
    print("   • Cryptographic storage proofs")
    print("   • Pay-per-use model")
    print("   • No monthly subscriptions")
    print("   • Large storage capacity")
    print("   • Sovereign data control")
    print()
    print("   📋 Cons:")
    print("   • Complex setup process")
    print("   • Requires approval/registration")
    print("   • Alpha software (may have bugs)")
    print("   • Need testnet tokens")
    print("   • Technical knowledge required")
    print("   • May not work immediately")
    print()
    print(
        f"   {Colors.CYAN}Best for:{Colors.END} Advanced developers, decentralization advocates"
    )
    print(f"   {Colors.CYAN}Cost:{Colors.END} Pay-per-use (very cheap)")
    print()


def print_use_case_guide():
    """Show use case recommendations"""
    print(f"{Colors.MAGENTA}{Colors.BOLD}🎯 WHICH SHOULD YOU CHOOSE?{Colors.END}")
    print("=" * 50)
    print()

    print(f"{Colors.GREEN}{Colors.BOLD}Choose PINATA if you:{Colors.END}")
    print("✅ Want to start uploading NFTs immediately")
    print("✅ Are building a prototype or MVP")
    print("✅ Need reliable, proven technology")
    print("✅ Don't want to deal with complex setup")
    print("✅ Are new to blockchain/IPFS")
    print("✅ Need customer support")
    print("✅ Want to focus on your app, not infrastructure")
    print()

    print(f"{Colors.BLUE}{Colors.BOLD}Choose FILECOIN CLOUD if you:{Colors.END}")
    print("✅ Are an experienced blockchain developer")
    print("✅ Value true decentralization above all")
    print("✅ Have time for complex setup and troubleshooting")
    print("✅ Want to contribute to cutting-edge technology")
    print("✅ Need very large storage capacity")
    print("✅ Don't mind alpha software limitations")
    print("✅ Understand Filecoin ecosystem well")
    print()


def get_user_preferences():
    """Get user preferences through interactive questions"""
    print(f"{Colors.CYAN}{Colors.BOLD}🤔 LET'S FIND YOUR IDEAL PROVIDER{Colors.END}")
    print("Answer a few questions to get a personalized recommendation:")
    print()

    score_pinata = 0
    score_filecoin = 0

    # Question 1: Experience level
    print("1. What's your experience with blockchain technology?")
    print("   a) Beginner - just getting started")
    print("   b) Intermediate - built a few projects")
    print("   c) Advanced - deep blockchain expertise")

    answer = input("   Your answer (a/b/c): ").strip().lower()
    if answer == "a":
        score_pinata += 3
    elif answer == "b":
        score_pinata += 1
        score_filecoin += 1
    elif answer == "c":
        score_filecoin += 2
    print()

    # Question 2: Timeline
    print("2. How quickly do you need to start uploading NFTs?")
    print("   a) Immediately - today or tomorrow")
    print("   b) This week")
    print("   c) I have time - next month is fine")

    answer = input("   Your answer (a/b/c): ").strip().lower()
    if answer == "a":
        score_pinata += 3
    elif answer == "b":
        score_pinata += 2
    elif answer == "c":
        score_filecoin += 1
    print()

    # Question 3: Project type
    print("3. What type of project are you building?")
    print("   a) Personal project or learning")
    print("   b) Startup/Business MVP")
    print("   c) Enterprise/Production system")

    answer = input("   Your answer (a/b/c): ").strip().lower()
    if answer == "a":
        score_pinata += 1
        score_filecoin += 1
    elif answer == "b":
        score_pinata += 2
    elif answer == "c":
        score_pinata += 2
        score_filecoin += 1
    print()

    # Question 4: Storage needs
    print("4. How much storage do you expect to need?")
    print("   a) Small - under 1GB")
    print("   b) Medium - 1-100GB")
    print("   c) Large - over 100GB")

    answer = input("   Your answer (a/b/c): ").strip().lower()
    if answer == "a":
        score_pinata += 2
    elif answer == "b":
        score_pinata += 1
    elif answer == "c":
        score_filecoin += 2
    print()

    # Question 5: Decentralization importance
    print("5. How important is true decentralization to you?")
    print("   a) Not important - just want it to work")
    print("   b) Somewhat important")
    print("   c) Very important - it's a core requirement")

    answer = input("   Your answer (a/b/c): ").strip().lower()
    if answer == "a":
        score_pinata += 2
    elif answer == "b":
        score_pinata += 1
        score_filecoin += 1
    elif answer == "c":
        score_filecoin += 3
    print()

    return score_pinata, score_filecoin


def show_recommendation(score_pinata: int, score_filecoin: int):
    """Show personalized recommendation based on scores"""
    print(
        f"{Colors.MAGENTA}{Colors.BOLD}🎯 YOUR PERSONALIZED RECOMMENDATION{Colors.END}"
    )
    print("=" * 50)

    if score_pinata > score_filecoin:
        print(f"{Colors.GREEN}{Colors.BOLD}🍍 RECOMMENDED: PINATA IPFS{Colors.END}")
        print()
        print("Based on your answers, Pinata IPFS is the best fit for you!")
        print()
        print(f"{Colors.CYAN}Why Pinata is perfect for you:{Colors.END}")
        print("• Quick and easy setup")
        print("• Reliable service you can depend on")
        print("• Perfect for your experience level")
        print("• Meets your timeline requirements")
        print()
        print(f"{Colors.GREEN}🚀 Next Step: Run the Pinata setup{Colors.END}")
        print("   python setup_pinata_alternative.py")

    elif score_filecoin > score_pinata:
        print(f"{Colors.BLUE}{Colors.BOLD}🌐 RECOMMENDED: FILECOIN CLOUD{Colors.END}")
        print()
        print("Based on your answers, Filecoin Cloud aligns with your goals!")
        print()
        print(f"{Colors.CYAN}Why Filecoin Cloud fits you:{Colors.END}")
        print("• You have the technical expertise")
        print("• Decentralization is important to you")
        print("• You're willing to invest time in setup")
        print("• You want cutting-edge technology")
        print()
        print(f"{Colors.YELLOW}⚠️  Important Notes:{Colors.END}")
        print("• Filecoin Cloud is currently in alpha")
        print("• Requires registration at https://filecoin.cloud/")
        print("• Setup can be complex and time-consuming")
        print("• You may need to troubleshoot issues")
        print()
        print(f"{Colors.BLUE}🚀 Next Steps:{Colors.END}")
        print("1. Register at https://filecoin.cloud/")
        print("2. Wait for approval (can take days/weeks)")
        print("3. Follow Filecoin Cloud setup guide")
        print()
        print(f"{Colors.CYAN}Alternative: Start with Pinata{Colors.END}")
        print("Consider using Pinata now and migrating to Filecoin later")

    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}🤔 IT'S A TIE!{Colors.END}")
        print()
        print("Both providers could work for you. Here's our suggestion:")
        print()
        print(f"{Colors.GREEN}🍍 Start with PINATA IPFS{Colors.END}")
        print("• Get your app working immediately")
        print("• Learn the NFT workflow")
        print("• Build and test your project")
        print()
        print(f"{Colors.BLUE}🌐 Migrate to FILECOIN CLOUD later{Colors.END}")
        print("• Once you're comfortable with the workflow")
        print("• When Filecoin Cloud exits alpha")
        print("• If decentralization becomes critical")


def show_setup_instructions():
    """Show setup instructions for each provider"""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}📋 SETUP INSTRUCTIONS{Colors.END}")
    print("=" * 50)
    print()

    print(f"{Colors.GREEN}{Colors.BOLD}For PINATA IPFS:{Colors.END}")
    print("1. Run: python setup_pinata_alternative.py")
    print("2. Get free API keys from https://app.pinata.cloud/")
    print("3. Follow the interactive setup")
    print("4. Start using your NFT app immediately!")
    print()

    print(f"{Colors.BLUE}{Colors.BOLD}For FILECOIN CLOUD:{Colors.END}")
    print("1. Register at https://filecoin.cloud/")
    print("2. Wait for approval (alpha access)")
    print("3. Get testnet tokens from faucet")
    print("4. Run: python setup_filecoin.py")
    print("5. Troubleshoot any issues")
    print()

    print(f"{Colors.CYAN}{Colors.BOLD}Current Status:{Colors.END}")
    print(f"• Pinata IPFS: {Colors.GREEN}✅ Ready to use{Colors.END}")
    print(f"• Filecoin Cloud: {Colors.YELLOW}⚠️  Alpha/Limited access{Colors.END}")


def main():
    """Main function"""
    print_header()

    print(f"{Colors.WHITE}This guide will help you choose the best storage provider")
    print(f"for your NFT project based on your specific needs.{Colors.END}")
    print()

    # Show comparison
    print_provider_comparison()
    print_use_case_guide()

    # Interactive recommendation
    try:
        print()
        do_quiz = (
            input(
                f"{Colors.CYAN}Would you like a personalized recommendation? (Y/n): {Colors.END}"
            )
            .strip()
            .lower()
        )

        if do_quiz != "n":
            print()
            pinata_score, filecoin_score = get_user_preferences()
            show_recommendation(pinata_score, filecoin_score)

        print()
        show_setup_instructions()

        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 READY TO GET STARTED?{Colors.END}")
        print()
        print("Run one of these commands to begin setup:")
        print(
            f"• {Colors.GREEN}python setup_pinata_alternative.py{Colors.END}  (recommended)"
        )
        print(
            f"• {Colors.BLUE}python setup_filecoin.py{Colors.END}           (advanced)"
        )
        print()
        print("Questions? Check the documentation in README.md")

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Selection cancelled by user.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")


if __name__ == "__main__":
    main()
