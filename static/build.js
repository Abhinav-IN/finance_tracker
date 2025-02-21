const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

const baseUrl = "https://vrchive.nomieze.com"; // Replace with your website's base URL
const srcPath = "./";
const cssFileName = "styles.css";

function buildCSSForFolder(folderPath) {
  const content = `${folderPath}/**/*.{html,js}`;
  const output = path.join(folderPath, cssFileName);
  const command = `npx tailwindcss -c ./tailwind.config.js --content ${content} -i "./src/css/styles.css" -o ${output} --minify`;

  exec(command, (err, stdout, stderr) => {
    if (err) {
      console.error(`Error building CSS for ${folderPath}: ${stderr}`);
    } else {
      console.log(`CSS built for ${folderPath}: ${stdout}`);
      // updateHTMLFiles(folderPath);
    }
  });
}

function processFolder(folderPath) {
  buildCSSForFolder(folderPath);

  fs.readdir(folderPath, (err, items) => {
    if (
      folderPath === "node_modules" ||
      folderPath === "node_modules" ||
      folderPath === "src" ||
      folderPath === ".git" ||
      folderPath === ".VSCodeCounter"
    ) {
      return;
    }
    console.log("starting build for: " + folderPath);
    if (err) throw err;

    items.forEach((item) => {
      const itemPath = path.join(folderPath, item);
      if (fs.lstatSync(itemPath).isDirectory()) {
        processFolder(itemPath);
      }
    });
  });
}

// function generateSitemap() {
//   let sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n`;
//   sitemap += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

//   // Function to recursively traverse directories and add URLs to sitemap
//   function traverseDirectory(directoryPath) {
//     const items = fs.readdirSync(directoryPath);

//     items.forEach((item) => {
//       const itemPath = path.join(directoryPath, item);
//       const stat = fs.statSync(itemPath);

//       if (stat.isDirectory()) {
//         traverseDirectory(itemPath);
//       } else if (path.extname(item) === ".html") {
//         const relativePath = path.relative(srcPath, itemPath);
//         const url = `${baseUrl}/${relativePath}`;
//         const lastmod = stat.mtime.toISOString().split("T")[0]; // Last modified date

//         sitemap += `  <url>\n`;
//         sitemap += `    <loc>${url}</loc>\n`;
//         sitemap += `    <lastmod>${lastmod}</lastmod>\n`;
//         sitemap += `  </url>\n`;
//       }
//     });
//   }

//   traverseDirectory(srcPath);

//   sitemap += `</urlset>`;
//   return sitemap;
// }

// // const sitemapContent = generateSitemap();
// // const sitemapPath = path.join(srcPath, "sitemap.xml");

// // fs.writeFileSync(sitemapPath, sitemapContent, "utf-8");
// // console.log(`Sitemap generated at ${sitemapPath}`);
// generateSitemap();

processFolder(srcPath);
