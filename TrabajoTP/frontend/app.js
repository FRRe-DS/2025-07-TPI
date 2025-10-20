// En app.js

// Espera a que todo el HTML esté cargado
document.addEventListener('DOMContentLoaded', () => {
    cargarProductos();
});

// Función para llamar a tu API de Django y mostrar los productos
async function cargarProductos() {
    // La URL de tu API de Django
    const API_URL = 'http://127.0.0.1:8000/api/product/';
    
    // Busca el contenedor donde irán los productos
    const container = document.querySelector('.product-container');
    
    // Muestra un mensaje de carga
    container.innerHTML = '<h2>Cargando productos...</h2>';

    try {
        const response = await fetch(API_URL);
        
        // Si la respuesta NO es exitosa (ej. error 502 o 404)
        if (!response.ok) {
            // Lee el JSON de error que envía tu API
            const errorData = await response.json();
            throw new Error(errorData.error || 'No se pudo cargar los productos.');
        }

        // Si la respuesta es exitosa, la convierte a JSON
        const productos = await response.json();

        // Limpia el mensaje de "Cargando..."
        container.innerHTML = '';

        // Si no hay productos, muestra un mensaje
        if (productos.length === 0) {
            container.innerHTML = '<p>No hay productos disponibles en este momento.</p>';
            return;
        }

        // Dibuja cada producto en el HTML
        productos.forEach(producto => {
            const card = document.createElement('article');
            card.className = 'product__card'; //
            
            // Usamos la plantilla de tu index.html
            card.innerHTML = `
                <div class="product__img-container">
                    <img class="product__img" src="${producto.imagen_url || 'https://via.placeholder.com/150'}" alt="${producto.nombre}">
                </div>
                <div class="product__info">
                    <h3>${producto.nombre}</h3>
                    <p>$${producto.precio}</p>
                </div>
                <button class="btn btn-add">Añadir al carrito</button>
            `;
            
            container.appendChild(card);
        });

    } catch (error) {
        // Muestra el error en la página
        container.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        console.error("Error al cargar productos:", error);
    }
}