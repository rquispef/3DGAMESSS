let scene, camera, renderer, controls;
let zombies = [];
let bullets = [];
let score = 0;

init();
animate();

function init() {
    // Escena
    scene = new THREE.Scene();

    // Cámara
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.6, 0); // Altura del jugador

    // Renderizador
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Controles
    controls = new THREE.PointerLockControls(camera, document.body);
    scene.add(controls.getObject());

    // Luz
    const light = new THREE.AmbientLight(0xffffff);
    scene.add(light);

    // Terreno
    const geometry = new THREE.BoxGeometry(10, 0.1, 10);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const ground = new THREE.Mesh(geometry, material);
    ground.position.y = -0.05;
    scene.add(ground);

    // Zombis
    createZombies(5);

    // Eventos
    document.addEventListener('click', () => {
        controls.lock();
    });

    window.addEventListener('resize', onWindowResize, false);
}

function createZombies(count) {
    const geometry = new THREE.BoxGeometry(0.5, 1, 0.5);
    const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });

    for (let i = 0; i < count; i++) {
        const zombie = new THREE.Mesh(geometry, material);
        zombie.position.set(Math.random() * 10 - 5, 0.5, Math.random() * 10 - 5);
        zombies.push(zombie);
        scene.add(zombie);
    }
}

function shoot() {
    const bulletGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const bulletMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });
    const bullet = new THREE.Mesh(bulletGeometry, bulletMaterial);
    bullet.position.copy(camera.position);
    bullet.velocity = new THREE.Vector3();
    bullet.velocity.copy(camera.getWorldDirection(new THREE.Vector3())).multiplyScalar(5);
    bullets.push(bullet);
    scene.add(bullet);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);

    // Movimiento de zombis
    zombies.forEach(zombie => {
        const direction = new THREE.Vector3();
        direction.subVectors(controls.getObject().position, zombie.position).normalize();
        zombie.position.add(direction.multiplyScalar(0.01));
    });

    // Actualización de balas
    bullets.forEach((bullet, index) => {
        bullet.position.add(bullet.velocity);
        if (bullet.position.length() > 50) {
            scene.remove(bullet);
            bullets.splice(index