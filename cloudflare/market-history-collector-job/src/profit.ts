import { Formula, Product, TradingPrices } from "./types";

const formulas: Record<Product, Formula> = {
    lead: { work: 1 },
    coca: { work: 1 },
    iron: { work: 1 },
    fish: { work: 40 },
    livestock: { work: 20 },
    grain: { work: 1 },
    limestone: { work: 1 },
    lightAmmo: { work: 1, rawMaterial: 'lead', rawMaterialAmount: 1 },
    bread: { work: 10, rawMaterial: 'grain', rawMaterialAmount: 10 },
    steel: { work: 10, rawMaterial: 'iron', rawMaterialAmount: 10 },
    concrete: { work: 10, rawMaterial: 'limestone', rawMaterialAmount: 10 },
    ammo: { work: 4, rawMaterial: 'lead', rawMaterialAmount: 4 },
    steak: { work: 20, rawMaterial: 'livestock', rawMaterialAmount: 1 },
    heavyAmmo: { work: 16, rawMaterial: 'lead', rawMaterialAmount: 16 },
    cocain: { work: 200, rawMaterial: 'coca', rawMaterialAmount: 200 },
    cookedFish: { work: 40, rawMaterial: 'fish', rawMaterialAmount: 1 },
};

export const calculateProfit = (prices: TradingPrices, product: Product): number => {
    const formula = formulas[product];
    if (!formula) {
        throw new Error(`No formula found for product: ${product}`);
    }

    const rawMaterialCost = formula.rawMaterial
        ? prices[formula.rawMaterial] * (formula.rawMaterialAmount || 1)
        : 0;

    const profit = (prices[product] - rawMaterialCost) / formula.work;

    return profit;
}
