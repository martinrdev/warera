/**
 * Welcome to Cloudflare Workers!
 *
 * This is a template for a Scheduled Worker: a Worker that can run on a
 * configurable interval:
 * https://developers.cloudflare.com/workers/platform/triggers/cron-triggers/
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Run `curl "http://localhost:8787/__scheduled?cron=*+*+*+*+*"` to see your Worker in action
 * - Run `npm run deploy` to publish your Worker
 *
 * Bind resources to your Worker in `wrangler.jsonc`. After adding bindings, a type definition for the
 * `Env` object can be regenerated with `npm run cf-typegen`.
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

import { calculateProfit } from "./profit";
import { availableProducts, ExtendedProduct, Product, TradingPricesResult } from "./types";

export interface Env {
	DB: D1Database;
}

export default {
	async fetch(req) {
		const url = new URL(req.url);
		url.pathname = '/__scheduled';
		url.searchParams.append('cron', '* * * * *');
		return new Response(`To test the scheduled handler, ensure you have used the "--test-scheduled" then try running "curl ${url.href}".`);
	},

	// The scheduled handler is invoked at the interval set in our wrangler.jsonc's
	// [[triggers]] configuration.
	async scheduled(event, env: Env, ctx): Promise<void> {
		// A Cron Trigger can make requests to other endpoints on the Internet,
		// publish to a Queue, query a D1 Database, and much more.
		//
		// We'll keep it simple and make an API call to a Cloudflare API:
		let resp = await fetch('https://api2.warera.io/trpc/itemTrading.getPrices');
		let wasSuccessful;

		if (resp.ok) {
			wasSuccessful = 'success';

			const result = await resp.json() as TradingPricesResult;
			const { result: { data } } = result;
			const timestamp = Date.now();

			// save market history
			const psMarket = env.DB.prepare(`INSERT INTO marketHistory (product, timestamp, price) VALUES (?, ?, ?)`);
			const queriesMarket = Object.entries(data).map(([product, price]) => psMarket.bind(product, timestamp, price));
			await env.DB.batch(queriesMarket);

			// save profit history
			const psProfit = env.DB.prepare(`INSERT INTO profitHistory (product, timestamp, workUnitProfit) VALUES (?, ?, ?)`);
			const queriesProfit = (Object.keys(data) as ExtendedProduct[])
				.filter((product) => availableProducts.includes(product as any))
				.map((product) => psProfit.bind(product, timestamp, calculateProfit(data, product as Product)));
			await env.DB.batch(queriesProfit);
		} else {
			wasSuccessful = 'fail';
		}

		// You could store this result in KV, write to a D1 Database, or publish to a Queue.
		// In this template, we'll just log the result:
		console.log(`trigger fired at ${event.cron}: ${wasSuccessful}`);
	},
} satisfies ExportedHandler<Env>;
