const https = require('https');
const AWS = require('aws-sdk');
const appsyncUrl = process.env.API_URL; 
const appsyncApiKey = process.env.API_KEY; 

exports.handler = async (event) => {
    const stockSymbol = 'AAPL'; // Example stock symbol
    const apiUrl = `https://api.example.com/stock/${stockSymbol}/price`; // Replace with actual stock API URL

    // Fetch the stock price
    const stockPrice = await new Promise((resolve, reject) => {
        https.get(apiUrl, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => resolve(JSON.parse(data).price));
        }).on('error', reject);
    });

    // Update DynamoDB via AppSync
    const mutation = `
        mutation UpdateStockPrice($input: UpdateStockPriceInput!) {
            updateStockPrice(input: $input) {
                id
                symbol
                price
                timestamp
            }
        }
    `;

    const variables = {
        input: {
            id: '1', // Example ID, use unique ID for different stocks
            symbol: stockSymbol,
            price: stockPrice,
            timestamp: new Date().toISOString(),
        },
    };

    const requestOptions = {
        hostname: new URL(appsyncUrl).hostname,
        path: '/graphql',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': appsyncApiKey,
        },
    };

    await new Promise((resolve, reject) => {
        const req = https.request(requestOptions, (res) => {
            res.on('data', (d) => process.stdout.write(d));
            res.on('end', resolve);
        });
        req.on('error', reject);
        req.write(JSON.stringify({ query: mutation, variables }));
        req.end();
    });

    return { statusCode: 200, body: JSON.stringify('Success') };
};
