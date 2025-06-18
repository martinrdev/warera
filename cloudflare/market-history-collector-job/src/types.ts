export const availableProducts = [
    'lead',
    'coca',
    'iron',
    'fish',
    'livestock',
    'grain',
    'limestone',
    'lightAmmo',
    'bread',
    'steel',
    'concrete',
    'ammo',
    'steak',
    'heavyAmmo',
    'cocain',
    'cookedFish',
] as const;

export type Product = typeof availableProducts[number];

export type ExtendedProduct = Product | 'case1';

export type TradingPrices = Record<ExtendedProduct, number>;

export interface TradingPricesResult {
    result: {
        data: TradingPrices;
    };
}

export interface Formula {
    work: number;
    rawMaterial?: Product;
    rawMaterialAmount?: number;
}
