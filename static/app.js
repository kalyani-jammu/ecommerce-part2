const grid = document.querySelector("#products");
const statusLine = document.querySelector("#status");
const searchInput = document.querySelector("#search");
const dialog = document.querySelector("#details");
const detailContent = document.querySelector("#detail-content");
let searchTimer;

function money(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(value);
}
function safeText(value) {
  return String(value ?? "");
}
function makeCard(product) {
  const article = document.createElement("article");
  article.className = "product-card";
  const image = document.createElement("img");
  image.src = product.image_url;
  image.alt = product.name;
  image.loading = "lazy";
  const info = document.createElement("div");
  info.className = "product-info";
  const title = document.createElement("h2");
  title.textContent = product.name;
  const desc = document.createElement("p");
  desc.textContent = product.description;
  const price = document.createElement("div");
  price.className = "price";
  price.textContent = money(product.price);
  const button = document.createElement("button");
  button.className = "details-button";
  button.textContent = "View details";
  button.addEventListener("click", () => showDetails(product.id));
  info.append(title, desc, price, button);
  article.append(image, info);
  return article;
}
async function loadProducts(search = "") {
  statusLine.textContent = "Loading products…";
  grid.replaceChildren();
  try {
    const response = await fetch(`/api/products?search=${encodeURIComponent(search)}`);
    if (!response.ok) throw new Error("Product request failed");
    const products = await response.json();
    if (!products.length) {
      statusLine.textContent = "";
      const message = document.createElement("p");
      message.className = "empty";
      message.textContent = "No matching products. Try another search.";
      grid.append(message);
      return;
    }
    products.forEach(product => grid.append(makeCard(product)));
    statusLine.textContent = `${products.length} product(s) found`;
  } catch {
    statusLine.textContent = "Could not load products. Please check that the server is running.";
  }
}
async function showDetails(id) {
  try {
    const response = await fetch(`/api/products/${id}`);
    const product = await response.json();
    if (!response.ok) throw new Error(product.error || "Could not load product.");
    detailContent.replaceChildren();
    const heading = document.createElement("h2");
    heading.textContent = product.name;
    const image = document.createElement("img");
    image.src = product.image_url;
    image.alt = product.name;
    const description = document.createElement("p");
    description.textContent = product.description;
    const price = document.createElement("p");
    price.className = "price";
    price.textContent = money(product.price);
    detailContent.append(heading, image, description, price);
    dialog.showModal();
  } catch (error) {
    statusLine.textContent = error.message;
  }
}
document.querySelector("#close-dialog").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", event => {
  if (event.target === dialog) dialog.close();
});
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadProducts(searchInput.value.trim()), 250);
});
loadProducts();
