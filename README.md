# 🚀 Cross-Gate Gamerch Recipe Scraper (CG Gamerch Spider)

A powerful Python web scraper tailored for retrieving equipment crafting recipes from the Gamerch Wiki for *Cross-Gate* (魔力寶貝) fan-made web tools. 

## 🌟 The Challenge & Our Solution
The target website (Gamerch) utilizes a highly chaotic HTML table structure. Instead of keeping crafting materials and their quantities together, the site flattens the table, separating material names and numbers into detached elements, mixed in with equipment stats and shop prices.

Standard cell-counting methods (`td[2]`, `td[3]`) completely fail here. To solve this, this script discards rigid structural mapping and implements a custom **"Array Pointer Alignment Algorithm"**. It flattens the table text into an indexable list, dynamically separates strings from integers, and maps names to quantities with 100% precision—regardless of how warped the layout is.

## 📦 Supported Item Categories
- **Weapons**: Sword, Axe, Spear, Staff, Bow, Throwing Weapon, Knife, Boomerang
- **Armor**: Shield, Armor (鎧甲), Clothing (衣服), Hat, Helmet, Robe, Shoes, Boots

## 🛠️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/cg-gamerch-spider.git](https://github.com/YOUR_USERNAME/cg-gamerch-spider.git)
   cd cg-gamerch-spider
