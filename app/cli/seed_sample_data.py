import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.cli.reset_database import reset_database
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.categoria import Categoria
from app.models.combo import Combo
from app.models.oferta import Oferta
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.user import User
from app.services.pedido import PedidoService


DEMO_EMAIL = "demo@orbita.local"
DEMO_PASSWORD = "demo123"


def _img(photo_id: str) -> str:
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1200&q=80"


CATEGORY_DATA = [
    {
        "key": "smartphones",
        "nombre": "Smartphones",
        "descripcion": "Telefonos 5G, equipos compactos y modelos premium.",
        "url_img": _img("photo-1511707171634-5f897ff02aa9"),
    },
    {
        "key": "laptops",
        "nombre": "Laptops",
        "descripcion": "Portatiles para estudio, oficina, gaming y creacion.",
        "url_img": _img("photo-1496181133206-80ce9b88a853"),
    },
    {
        "key": "tablets",
        "nombre": "Tablets",
        "descripcion": "Tablets para notas, dibujo, consumo y productividad.",
        "url_img": _img("photo-1544244015-0df4b3ffc6b0"),
    },
    {
        "key": "audio",
        "nombre": "Audio",
        "descripcion": "Audifonos, earbuds, bocinas y barras de sonido.",
        "url_img": _img("photo-1505740420928-5e560c06d30e"),
    },
    {
        "key": "gaming",
        "nombre": "Gaming",
        "descripcion": "Consolas, controles y perifericos para jugar.",
        "url_img": _img("photo-1606144042614-b2417e99c4e3"),
    },
    {
        "key": "accesorios",
        "nombre": "Accesorios",
        "descripcion": "Cargadores, hubs, webcams y accesorios de setup.",
        "url_img": _img("photo-1527864550417-7fd91fc51a46"),
    },
    {
        "key": "smart_home",
        "nombre": "Smart Home",
        "descripcion": "Dispositivos conectados para automatizar el hogar.",
        "url_img": _img("photo-1558002038-1055907df827"),
    },
    {
        "key": "monitores",
        "nombre": "Monitores",
        "descripcion": "Pantallas 4K, ultrawide y gaming para cualquier escritorio.",
        "url_img": _img("photo-1527443224154-c4a3942d3acf"),
    },
]


PRODUCT_DATA = [
    {
        "key": "smartphone_nova_x1",
        "categoria": "smartphones",
        "nombre": "Smartphone Nova X1 5G",
        "descripcion": "Pantalla OLED de 6.5 pulgadas, 128 GB y camara nocturna.",
        "precio": "699.00",
        "url_img": _img("photo-1511707171634-5f897ff02aa9"),
    },
    {
        "key": "smartphone_pixelario_8",
        "categoria": "smartphones",
        "nombre": "Smartphone Pixelario 8",
        "descripcion": "Equipo premium con fotografia computacional y carga rapida.",
        "precio": "849.00",
        "url_img": _img("photo-1510557880182-3d4d3cba35a5"),
    },
    {
        "key": "smartphone_compact_5g",
        "categoria": "smartphones",
        "nombre": "Smartphone Compact 5G",
        "descripcion": "Telefono ligero con bateria de larga duracion y doble SIM.",
        "precio": "499.00",
        "url_img": _img("photo-1523206489230-c012c64b2b48"),
    },
    {
        "key": "smartphone_fold_vision",
        "categoria": "smartphones",
        "nombre": "Smartphone Fold Vision",
        "descripcion": "Pantalla plegable, 256 GB y modo multitarea avanzado.",
        "precio": "1199.00",
        "url_img": _img("photo-1546054454-aa26e2b734c7"),
    },
    {
        "key": "laptop_ultrabook_air_14",
        "categoria": "laptops",
        "nombre": "Laptop Ultrabook Air 14",
        "descripcion": "Portatil delgada con SSD de 512 GB y autonomia para todo el dia.",
        "precio": "1099.00",
        "url_img": _img("photo-1517336714731-489689fd1ca8"),
    },
    {
        "key": "laptop_workstation_pro_16",
        "categoria": "laptops",
        "nombre": "Laptop Workstation Pro 16",
        "descripcion": "Equipo potente para desarrollo, diseno y renderizado.",
        "precio": "1899.00",
        "url_img": _img("photo-1496181133206-80ce9b88a853"),
    },
    {
        "key": "laptop_gamer_rtx_15",
        "categoria": "laptops",
        "nombre": "Laptop Gamer RTX 15",
        "descripcion": "GPU dedicada, pantalla 144 Hz y teclado retroiluminado.",
        "precio": "1599.00",
        "url_img": _img("photo-1498050108023-c5249f4df085"),
    },
    {
        "key": "laptop_estudiante_13",
        "categoria": "laptops",
        "nombre": "Laptop Estudiante 13",
        "descripcion": "Equipo liviano para clases, documentos y videollamadas.",
        "precio": "749.00",
        "url_img": _img("photo-1484788984921-03950022c9ef"),
    },
    {
        "key": "tablet_studio_11",
        "categoria": "tablets",
        "nombre": "Tablet Studio 11",
        "descripcion": "Tablet con lapiz digital para bocetos, notas y lectura.",
        "precio": "699.00",
        "url_img": _img("photo-1544244015-0df4b3ffc6b0"),
    },
    {
        "key": "tablet_mini_note",
        "categoria": "tablets",
        "nombre": "Tablet Mini Note",
        "descripcion": "Formato compacto para apuntes, libros y contenido movil.",
        "precio": "399.00",
        "url_img": _img("photo-1516321318423-f06f85e504b3"),
    },
    {
        "key": "tablet_pro_129",
        "categoria": "tablets",
        "nombre": "Tablet Pro 12.9",
        "descripcion": "Pantalla grande, alto brillo y accesorios de productividad.",
        "precio": "999.00",
        "url_img": _img("photo-1585792180666-f7347c490ee2"),
    },
    {
        "key": "lector_eink_plus",
        "categoria": "tablets",
        "nombre": "Lector E-Ink Plus",
        "descripcion": "Pantalla de tinta electronica con luz calida ajustable.",
        "precio": "219.00",
        "url_img": _img("photo-1561154464-82e9adf32764"),
    },
    {
        "key": "audifonos_noise_cancel_pro",
        "categoria": "audio",
        "nombre": "Audifonos Noise Cancel Pro",
        "descripcion": "Cancelacion activa de ruido y 30 horas de bateria.",
        "precio": "199.00",
        "url_img": _img("photo-1505740420928-5e560c06d30e"),
    },
    {
        "key": "earbuds_true_wireless",
        "categoria": "audio",
        "nombre": "Earbuds True Wireless",
        "descripcion": "Estuche de carga, resistencia al sudor y modo ambiente.",
        "precio": "129.00",
        "url_img": _img("photo-1606220588913-b3aacb4d2f46"),
    },
    {
        "key": "bocina_soundcube",
        "categoria": "audio",
        "nombre": "Bocina Bluetooth SoundCube",
        "descripcion": "Bocina portatil resistente al agua con sonido 360.",
        "precio": "89.00",
        "url_img": _img("photo-1545454675-3531b543be5d"),
    },
    {
        "key": "barra_sonido_cinema",
        "categoria": "audio",
        "nombre": "Barra de Sonido Cinema",
        "descripcion": "Sonido envolvente para TV con subwoofer inalambrico.",
        "precio": "299.00",
        "url_img": _img("photo-1608043152269-423dbba4e7e1"),
    },
    {
        "key": "consola_nextgen",
        "categoria": "gaming",
        "nombre": "Consola NextGen 1 TB",
        "descripcion": "Consola de sobremesa con SSD rapido y control inalambrico.",
        "precio": "499.00",
        "url_img": _img("photo-1606144042614-b2417e99c4e3"),
    },
    {
        "key": "control_wireless_pro",
        "categoria": "gaming",
        "nombre": "Control Wireless Pro",
        "descripcion": "Control ergonomico con vibracion HD y USB-C.",
        "precio": "69.00",
        "url_img": _img("photo-1593305841991-05c297ba4575"),
    },
    {
        "key": "teclado_mecanico_rgb",
        "categoria": "gaming",
        "nombre": "Teclado Mecanico RGB",
        "descripcion": "Switches tactiles, iluminacion por tecla y reposamunecas.",
        "precio": "119.00",
        "url_img": _img("photo-1550745165-9bc0b252726f"),
    },
    {
        "key": "mouse_gamer_precision",
        "categoria": "gaming",
        "nombre": "Mouse Gamer Precision",
        "descripcion": "Sensor de alta precision, botones laterales y RGB.",
        "precio": "59.00",
        "url_img": _img("photo-1615663245857-ac93bb7c39e7"),
    },
    {
        "key": "consola_portatil_play",
        "categoria": "gaming",
        "nombre": "Consola Portatil Play",
        "descripcion": "Pantalla integrada, controles laterales y modo dock.",
        "precio": "399.00",
        "url_img": _img("photo-1612287230202-1ff1d85d1bdf"),
    },
    {
        "key": "cargador_usbc_100w",
        "categoria": "accesorios",
        "nombre": "Cargador USB-C 100W",
        "descripcion": "Cargador GaN compacto para laptop, tablet y smartphone.",
        "precio": "49.00",
        "url_img": _img("photo-1583394838336-acd977736f90"),
    },
    {
        "key": "power_bank_20000",
        "categoria": "accesorios",
        "nombre": "Power Bank 20000 mAh",
        "descripcion": "Bateria externa con carga rapida USB-C y pantalla digital.",
        "precio": "59.00",
        "url_img": _img("photo-1612815154858-60aa4c59eaa6"),
    },
    {
        "key": "hub_usbc_8en1",
        "categoria": "accesorios",
        "nombre": "Hub USB-C 8 en 1",
        "descripcion": "HDMI, Ethernet, SD y puertos USB para escritorio movil.",
        "precio": "69.00",
        "url_img": _img("photo-1593642632823-8f785ba67e45"),
    },
    {
        "key": "webcam_full_hd",
        "categoria": "accesorios",
        "nombre": "Webcam Full HD",
        "descripcion": "Camara 1080p con microfono dual para reuniones.",
        "precio": "79.00",
        "url_img": _img("photo-1587825140708-dfaf72ae4b04"),
    },
    {
        "key": "soporte_laptop_aluminio",
        "categoria": "accesorios",
        "nombre": "Soporte Laptop Aluminio",
        "descripcion": "Base elevada plegable para mejorar postura y ventilacion.",
        "precio": "45.00",
        "url_img": _img("photo-1527443195645-1133f7f28990"),
    },
    {
        "key": "parlante_inteligente_home",
        "categoria": "smart_home",
        "nombre": "Parlante Inteligente Home Mini",
        "descripcion": "Asistente de voz para musica, rutinas y control del hogar.",
        "precio": "99.00",
        "url_img": _img("photo-1543512214-318c7553f230"),
    },
    {
        "key": "camara_wifi_interior",
        "categoria": "smart_home",
        "nombre": "Camara WiFi Interior",
        "descripcion": "Camara 2K con vision nocturna, audio bidireccional y app.",
        "precio": "69.00",
        "url_img": _img("photo-1558002038-1055907df827"),
    },
    {
        "key": "bombillo_rgb_smart",
        "categoria": "smart_home",
        "nombre": "Bombillo Inteligente RGB",
        "descripcion": "Luz regulable con escenas, horarios y control por voz.",
        "precio": "19.00",
        "url_img": _img("photo-1558618666-fcd25c85cd64"),
    },
    {
        "key": "enchufe_smart_pack",
        "categoria": "smart_home",
        "nombre": "Enchufe Inteligente Pack 2",
        "descripcion": "Control remoto de equipos y medicion basica de consumo.",
        "precio": "29.00",
        "url_img": _img("photo-1558089687-f282ffcbc126"),
    },
    {
        "key": "robot_aspirador_smartclean",
        "categoria": "smart_home",
        "nombre": "Robot Aspirador SmartClean",
        "descripcion": "Mapeo inteligente, retorno automatico y app movil.",
        "precio": "299.00",
        "url_img": _img("photo-1585771724684-38269d6639fd"),
    },
    {
        "key": "router_mesh_wifi6",
        "categoria": "smart_home",
        "nombre": "Router Mesh WiFi 6",
        "descripcion": "Cobertura para toda la casa con dos nodos y control parental.",
        "precio": "249.00",
        "url_img": _img("photo-1606904825846-647eb07f5be2"),
    },
    {
        "key": "monitor_4k_27",
        "categoria": "monitores",
        "nombre": "Monitor 27 4K Ultra",
        "descripcion": "Panel IPS 4K con USB-C y colores calibrados.",
        "precio": "399.00",
        "url_img": _img("photo-1527443224154-c4a3942d3acf"),
    },
    {
        "key": "monitor_gaming_165",
        "categoria": "monitores",
        "nombre": "Monitor Gaming 27 165Hz",
        "descripcion": "Respuesta rapida, alta tasa de refresco y soporte ajustable.",
        "precio": "329.00",
        "url_img": _img("photo-1547082299-de196ea013d6"),
    },
    {
        "key": "monitor_curvo_ultrawide",
        "categoria": "monitores",
        "nombre": "Monitor Curvo 34 Ultrawide",
        "descripcion": "Formato 21:9 para multitarea, edicion y simuladores.",
        "precio": "599.00",
        "url_img": _img("photo-1593640408182-31c70c8268f5"),
    },
    {
        "key": "screenbar_monitor",
        "categoria": "monitores",
        "nombre": "Lampara Monitor ScreenBar",
        "descripcion": "Iluminacion frontal sin reflejos para escritorio nocturno.",
        "precio": "89.00",
        "url_img": _img("photo-1526925539332-aa3b66e35444"),
    },
]


OFFER_DATA = [
    {
        "nombre": "Upgrade Smartphone",
        "descripcion": "Descuento directo en smartphones 5G seleccionados.",
        "monto": "60.00",
        "imagen": _img("photo-1511707171634-5f897ff02aa9"),
        "dias": 21,
        "productos": [
            "smartphone_nova_x1",
            "smartphone_pixelario_8",
            "smartphone_compact_5g",
        ],
    },
    {
        "nombre": "Workspace Pro",
        "descripcion": "Oferta para laptops de productividad y monitores de escritorio.",
        "monto": "120.00",
        "imagen": _img("photo-1497366811353-6870744d04b2"),
        "dias": 30,
        "productos": [
            "laptop_ultrabook_air_14",
            "laptop_workstation_pro_16",
            "laptop_estudiante_13",
            "monitor_4k_27",
            "monitor_curvo_ultrawide",
        ],
    },
    {
        "nombre": "Audio Week",
        "descripcion": "Rebaja para audifonos, earbuds, bocinas y barras de sonido.",
        "monto": "25.00",
        "imagen": _img("photo-1505740420928-5e560c06d30e"),
        "dias": 14,
        "productos": [
            "audifonos_noise_cancel_pro",
            "earbuds_true_wireless",
            "bocina_soundcube",
            "barra_sonido_cinema",
        ],
    },
    {
        "nombre": "Gaming Night",
        "descripcion": "Ahorro en equipos y perifericos para setups gamer.",
        "monto": "40.00",
        "imagen": _img("photo-1550745165-9bc0b252726f"),
        "dias": 18,
        "productos": [
            "laptop_gamer_rtx_15",
            "consola_nextgen",
            "consola_portatil_play",
            "monitor_gaming_165",
        ],
    },
    {
        "nombre": "Casa Conectada",
        "descripcion": "Promocion en productos smart home para empezar a automatizar.",
        "monto": "18.00",
        "imagen": _img("photo-1558002038-1055907df827"),
        "dias": 25,
        "productos": [
            "parlante_inteligente_home",
            "camara_wifi_interior",
            "bombillo_rgb_smart",
            "enchufe_smart_pack",
            "robot_aspirador_smartclean",
            "router_mesh_wifi6",
        ],
    },
    {
        "nombre": "Accesorios Esenciales",
        "descripcion": "Descuento para completar tu mochila o escritorio tech.",
        "monto": "12.00",
        "imagen": _img("photo-1527864550417-7fd91fc51a46"),
        "dias": 12,
        "productos": [
            "cargador_usbc_100w",
            "power_bank_20000",
            "hub_usbc_8en1",
            "webcam_full_hd",
            "soporte_laptop_aluminio",
            "screenbar_monitor",
        ],
    },
]


COMBO_DATA = [
    {
        "key": "home_office_pro",
        "nombre": "Combo Home Office Pro",
        "descripcion": "Laptop, monitor 4K, webcam, hub USB-C y soporte de aluminio.",
        "precio": "1499.00",
        "imagen": _img("photo-1497366811353-6870744d04b2"),
        "productos": [
            "laptop_ultrabook_air_14",
            "monitor_4k_27",
            "webcam_full_hd",
            "hub_usbc_8en1",
            "soporte_laptop_aluminio",
        ],
    },
    {
        "key": "gamer_starter",
        "nombre": "Combo Gamer Starter",
        "descripcion": "Laptop gamer, monitor 165 Hz, teclado, mouse y audifonos.",
        "precio": "1999.00",
        "imagen": _img("photo-1550745165-9bc0b252726f"),
        "productos": [
            "laptop_gamer_rtx_15",
            "monitor_gaming_165",
            "teclado_mecanico_rgb",
            "mouse_gamer_precision",
            "audifonos_noise_cancel_pro",
        ],
    },
    {
        "key": "mobile_creator",
        "nombre": "Combo Creador Movil",
        "descripcion": "Smartphone premium, earbuds, power bank y cargador USB-C.",
        "precio": "979.00",
        "imagen": _img("photo-1510557880182-3d4d3cba35a5"),
        "productos": [
            "smartphone_pixelario_8",
            "earbuds_true_wireless",
            "power_bank_20000",
            "cargador_usbc_100w",
        ],
    },
    {
        "key": "smart_home_start",
        "nombre": "Combo Smart Home Start",
        "descripcion": "Parlante inteligente, camara, bombillo RGB y enchufes smart.",
        "precio": "179.00",
        "imagen": _img("photo-1558002038-1055907df827"),
        "productos": [
            "parlante_inteligente_home",
            "camara_wifi_interior",
            "bombillo_rgb_smart",
            "enchufe_smart_pack",
        ],
    },
    {
        "key": "student_pack",
        "nombre": "Combo Student Pack",
        "descripcion": "Laptop de estudiante, tablet mini, audifonos y cargador 100W.",
        "precio": "999.00",
        "imagen": _img("photo-1484788984921-03950022c9ef"),
        "productos": [
            "laptop_estudiante_13",
            "tablet_mini_note",
            "audifonos_noise_cancel_pro",
            "cargador_usbc_100w",
        ],
    },
    {
        "key": "cinema_room",
        "nombre": "Combo Cinema Room",
        "descripcion": "Barra de sonido, bocina Bluetooth, enchufes y luces RGB.",
        "precio": "369.00",
        "imagen": _img("photo-1608043152269-423dbba4e7e1"),
        "productos": [
            "barra_sonido_cinema",
            "bocina_soundcube",
            "enchufe_smart_pack",
            "bombillo_rgb_smart",
        ],
    },
]


def _has_existing_data(db: Session) -> bool:
    models = [User, Categoria, Producto, Oferta, Combo, Pedido]
    return any((db.scalar(select(func.count()).select_from(model)) or 0) for model in models)


def _create_categories(db: Session) -> dict[str, Categoria]:
    categories: dict[str, Categoria] = {}
    for item in CATEGORY_DATA:
        category = Categoria(
            nombre=item["nombre"],
            descripcion=item["descripcion"],
            url_img=item["url_img"],
        )
        db.add(category)
        categories[item["key"]] = category
    db.flush()
    return categories


def _create_products(
    db: Session,
    categories: dict[str, Categoria],
) -> dict[str, Producto]:
    products: dict[str, Producto] = {}
    for item in PRODUCT_DATA:
        product = Producto(
            nombre=item["nombre"],
            descripcion=item["descripcion"],
            precio_base=Decimal(item["precio"]),
            url_img=item["url_img"],
            categoria_id=categories[item["categoria"]].id,
        )
        db.add(product)
        products[item["key"]] = product
    db.flush()
    return products


def _create_offers(
    db: Session,
    products: dict[str, Producto],
    now: datetime,
) -> list[Oferta]:
    offers: list[Oferta] = []
    for item in OFFER_DATA:
        offer = Oferta(
            fecha_inicio=now - timedelta(days=1),
            fecha_fin=now + timedelta(days=item["dias"]),
            nombre=item["nombre"],
            descripcion=item["descripcion"],
            monto_descuento=Decimal(item["monto"]),
            imagen=item["imagen"],
        )
        offer.productos = [products[key] for key in item["productos"]]
        db.add(offer)
        offers.append(offer)
    db.flush()
    return offers


def _create_combos(db: Session, products: dict[str, Producto]) -> dict[str, Combo]:
    combos: dict[str, Combo] = {}
    for item in COMBO_DATA:
        combo = Combo(
            nombre=item["nombre"],
            descripcion=item["descripcion"],
            precio=Decimal(item["precio"]),
            imagen=item["imagen"],
        )
        combo.productos = [products[key] for key in item["productos"]]
        db.add(combo)
        combos[item["key"]] = combo
    db.flush()
    return combos


def _ensure_demo_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if user:
        return user

    user = User(
        email=DEMO_EMAIL,
        hashed_password=get_password_hash(DEMO_PASSWORD),
        full_name="Usuario Demo TechShop",
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _create_demo_orders(
    db: Session,
    products: dict[str, Producto],
    combos: dict[str, Combo],
) -> None:
    pedido_service = PedidoService(db)
    demo_orders: list[dict[str, Any]] = [
        {
            "nombre": "Ana Tech Demo",
            "telefono": "55512345",
            "productos": [
                {"producto_id": products["smartphone_nova_x1"].id, "cantidad": 1},
                {"producto_id": products["earbuds_true_wireless"].id, "cantidad": 1},
                {"producto_id": products["power_bank_20000"].id, "cantidad": 1},
            ],
            "combos": [{"combo_id": combos["mobile_creator"].id, "cantidad": 1}],
        },
        {
            "nombre": "Luis Gamer Demo",
            "telefono": "55567890",
            "productos": [
                {"producto_id": products["consola_nextgen"].id, "cantidad": 1},
                {"producto_id": products["control_wireless_pro"].id, "cantidad": 2},
                {"producto_id": products["monitor_gaming_165"].id, "cantidad": 1},
            ],
            "combos": [{"combo_id": combos["gamer_starter"].id, "cantidad": 1}],
        },
        {
            "nombre": "Marta Home Demo",
            "telefono": "55524680",
            "productos": [
                {"producto_id": products["robot_aspirador_smartclean"].id, "cantidad": 1},
                {"producto_id": products["router_mesh_wifi6"].id, "cantidad": 1},
            ],
            "combos": [{"combo_id": combos["smart_home_start"].id, "cantidad": 2}],
        },
    ]

    for order in demo_orders:
        pedido_service.create(**order)


def seed_sample_data(*, reset: bool = False, confirm_reset: bool = False, append: bool = False) -> None:
    if reset:
        reset_database(confirm=confirm_reset)

    with SessionLocal() as db:
        if not append and _has_existing_data(db):
            raise ValueError(
                "La base ya tiene datos. Usa --reset --yes para reemplazarlos "
                "o --append para agregar datos encima."
            )

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        categories = _create_categories(db)
        products = _create_products(db, categories)
        _create_offers(db, products, now)
        combos = _create_combos(db, products)
        _ensure_demo_user(db)
        db.commit()
        _create_demo_orders(db, products, combos)

    print("Datos de ejemplo TechShop creados.")
    print(f"Categorias: {len(CATEGORY_DATA)}")
    print(f"Productos: {len(PRODUCT_DATA)}")
    print(f"Ofertas: {len(OFFER_DATA)}")
    print(f"Combos: {len(COMBO_DATA)}")
    print(f"Usuario demo: {DEMO_EMAIL}")
    print(f"Password demo: {DEMO_PASSWORD}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Llena la base de datos con datos de ejemplo TechShop para frontend.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Vacia la base antes de sembrar datos.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma el reset cuando se usa --reset.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Agrega datos aunque la base ya tenga contenido.",
    )
    args = parser.parse_args()

    seed_sample_data(reset=args.reset, confirm_reset=args.yes, append=args.append)


if __name__ == "__main__":
    main()
