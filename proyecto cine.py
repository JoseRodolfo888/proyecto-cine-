import tkinter as tk
from tkinter import ttk, messagebox,simpledialog,scrolledtext
import mysql.connector
from datetime import datetime, timedelta
import getpass
import sys
from prettytable import PrettyTable


class CineManager:
    def __init__(self, root):
        self.root = root
        self.root.title("CineMagic Premium - Sistema de Gestión")
        self.root.geometry("1000x700")
        
        # Configuración de estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Conexión a la base de datos
        self.conectar_bd()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def conectar_bd(self):
        """Inicializa la conexión con la base de datos"""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="123456",
                database="cine"
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al conectar a la base de datos: {err}")
            sys.exit(1)
    
    def crear_interfaz(self):
        """Crea los elementos principales de la interfaz"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de título
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(title_frame, text="・.・CineMagic Premium ・.・", style='Header.TLabel').pack()
        ttk.Label(title_frame, text="Sistema de Gestión Cinematográfica Completo").pack()
        ttk.Label(title_frame, text="Versión 3.0 - Panel Administrativo y Cliente").pack()
        
        # Frame de contenido
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mostrar menú principal inicial
        self.mostrar_menu_principal()
    
    def limpiar_contenido(self):
        """Limpia el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="MENÚ PRINCIPAL", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Iniciar sesión", self.iniciar_sesion),
            ("Registrarse", self.registrar_usuario),
            ("Ver cartelera", self.mostrar_cartelera),
            ("Salir", self.salir)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=20).pack(pady=5)
    
    def iniciar_sesion(self):
        """Interfaz para iniciar sesión"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="INICIO DE SESIÓN", style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        ttk.Label(self.content_frame, text="Correo electrónico:").pack()
        self.correo_entry = ttk.Entry(self.content_frame, width=30)
        self.correo_entry.pack(pady=5)
        
        ttk.Label(self.content_frame, text="Contraseña:").pack()
        self.contraseña_entry = ttk.Entry(self.content_frame, width=30, show="*")
        self.contraseña_entry.pack(pady=5)
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Iniciar sesión", command=self.validar_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
    
    def validar_login(self):
        """Valida las credenciales del usuario"""
        correo = self.correo_entry.get()
        contraseña = self.contraseña_entry.get()
        
        query = """
        SELECT u.*, r.nombre as rol 
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.correo = %s AND u.contraseña = %s
        """
        self.cursor.execute(query, (correo, contraseña))
        usuario = self.cursor.fetchone()
        
        if usuario:
            messagebox.showinfo("Bienvenido", f"¡Bienvenido/a, {usuario['nombre']} ({usuario['rol']})!")
            if usuario['id_rol'] == 1:  # Administrador
                self.mostrar_menu_administrador()
            else:
                self.mostrar_menu_usuario(usuario)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas. Intente nuevamente.")
    
    def registrar_usuario(self):
        """Interfaz para registrar un nuevo usuario"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="REGISTRO DE USUARIO", style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        fields = [
            ("Nombre completo:", "nombre_entry"),
            ("Edad:", "edad_entry"),
            ("Correo electrónico:", "correo_entry"),
            ("Contraseña (mínimo 6 caracteres):", "contraseña_entry")
        ]
        
        self.entries = {}
        for text, name in fields:
            ttk.Label(self.content_frame, text=text).pack()
            entry = ttk.Entry(self.content_frame, width=30)
            if "contraseña" in name:
                entry.config(show="*")
            entry.pack(pady=5)
            self.entries[name] = entry
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Registrarse", command=self.procesar_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Regresar", command=self.mostrar_menu_principal).pack(side=tk.LEFT, padx=5)
    
    def procesar_registro(self):
        """Procesa el registro de un nuevo usuario"""
        nombre = self.entries['nombre_entry'].get()
        edad = self.entries['edad_entry'].get()
        correo = self.entries['correo_entry'].get()
        contraseña = self.entries['contraseña_entry'].get()
        
        # Validaciones
        if not nombre.strip():
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return
        
        try:
            edad = int(edad)
            if not (5 <= edad <= 100):
                messagebox.showerror("Error", "La edad debe estar entre 5 y 100 años.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese una edad válida.")
            return
        
        if "@" not in correo or "." not in correo:
            messagebox.showerror("Error", "Ingrese un correo válido.")
            return
        
        if len(contraseña) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres.")
            return
        
        try:
            query = "INSERT INTO usuarios (nombre, edad, correo, contraseña, id_rol) VALUES (%s, %s, %s, %s, 2)"
            self.cursor.execute(query, (nombre, edad, correo, contraseña))
            self.conn.commit()
            messagebox.showinfo("Éxito", "¡Registro exitoso! Ahora puede iniciar sesión.")
            self.mostrar_menu_principal()
        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicado
                messagebox.showerror("Error", "El correo electrónico ya está registrado.")
            else:
                messagebox.showerror("Error", f"Error al registrar: {err}")
    
    def mostrar_cartelera(self):
        """Muestra las películas disponibles en cartelera"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="CARTELERA", style='Header.TLabel').pack(pady=10)
        
        query = """
        SELECT p.titulo, p.director, p.duracion, p.clasificacion, p.genero, 
               f.id_funcion, f.horario, s.nombre as sala, f.precio,
               COUNT(a.id_asiento) as asientos_disponibles
        FROM peliculas p
        JOIN funciones f ON p.id_pelicula = f.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
        WHERE f.horario > NOW()
        GROUP BY f.id_funcion
        ORDER BY f.horario
        """
        
        self.cursor.execute(query)
        funciones = self.cursor.fetchall()
        
        if not funciones:
            ttk.Label(self.content_frame, text="No hay funciones disponibles en este momento.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=10)
            return
        
        # Crear un frame con scroll para la cartelera
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mostrar cada función
        for funcion in funciones:
            frame_funcion = ttk.Frame(scrollable_frame, borderwidth=2, relief="groove", padding=10)
            frame_funcion.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(frame_funcion, text=f"🎞️ {funcion['titulo']}", font=('Arial', 11, 'bold')).pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Director: {funcion['director']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Duración: {funcion['duracion']} minutos").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Clasificación: {funcion['clasificacion']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Género: {funcion['genero']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Horario: {funcion['horario'].strftime('%d/%m/%Y %H:%M')}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Sala: {funcion['sala']}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Precio: ${funcion['precio']:.2f}").pack(anchor="w")
            ttk.Label(frame_funcion, text=f"Asientos disponibles: {funcion['asientos_disponibles']}").pack(anchor="w")
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", command=self.mostrar_menu_principal).pack(pady=10)
    
    def mostrar_menu_administrador(self):
        """Muestra el menú para administradores"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="PANEL DE ADMINISTRADOR", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Gestión de Películas", self.menu_gestion_peliculas),
            ("Gestión de Salas", self.menu_gestion_salas),
            ("Gestión de Funciones", self.menu_gestion_funciones),
            ("Gestión de Productos", self.menu_gestion_productos),
            ("Ver Reportes", self.mostrar_reportes),
            ("Cerrar sesión", self.mostrar_menu_principal)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def menu_gestion_peliculas(self):
        """Submenú para gestión de películas"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="GESTIÓN DE PELÍCULAS", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar película", self.agregar_pelicula),
            ("Editar película", self.editar_pelicula),
            ("Eliminar película", self.eliminar_pelicula),
            ("Ver todas las películas", self.mostrar_todas_peliculas),
            ("Buscar película", self.buscar_pelicula),
            ("Regresar", self.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def agregar_pelicula(self):
        """Interfaz para agregar una nueva película"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="AGREGAR PELÍCULA", style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        fields = [
            ("Título de la película:", "titulo_entry"),
            ("Director:", "director_entry"),
            ("Duración (minutos):", "duracion_entry"),
            ("Clasificación (ej. 'A', 'B', 'PG-13'):", "clasificacion_entry"),
            ("Género:", "genero_entry")
        ]
        
        self.entries = {}
        for text, name in fields:
            ttk.Label(self.content_frame, text=text).pack()
            entry = ttk.Entry(self.content_frame, width=30)
            entry.pack(pady=5)
            self.entries[name] = entry
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Guardar", command=self.guardar_pelicula).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.menu_gestion_peliculas).pack(side=tk.LEFT, padx=5)
    
    def guardar_pelicula(self):
        """Guarda una nueva película en la base de datos"""
        titulo = self.entries['titulo_entry'].get()
        director = self.entries['director_entry'].get() or "Desconocido"
        duracion = self.entries['duracion_entry'].get()
        clasificacion = self.entries['clasificacion_entry'].get() or "NR"
        genero = self.entries['genero_entry'].get() or "Otro"
        
        # Validaciones
        if not titulo.strip():
            messagebox.showerror("Error", "El título no puede estar vacío.")
            return
        
        try:
            duracion = int(duracion)
            if duracion <= 0:
                messagebox.showerror("Error", "La duración debe ser mayor a 0 en minutos.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la duración.")
            return
        
        try:
            query = """
            INSERT INTO peliculas (titulo, director, duracion, clasificacion, genero)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (titulo, director, duracion, clasificacion, genero))
            self.conn.commit()
            messagebox.showinfo("Éxito", f"¡Película '{titulo}' agregada exitosamente!")
            self.menu_gestion_peliculas()
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al agregar película: {err}")
    
    def mostrar_todas_peliculas(self):
        """Muestra todas las películas en el sistema"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="LISTA DE PELÍCULAS", style='Header.TLabel').pack(pady=10)
        
        self.cursor.execute("SELECT * FROM peliculas ORDER BY titulo")
        peliculas = self.cursor.fetchall()
        
        if not peliculas:
            ttk.Label(self.content_frame, text="No hay películas registradas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_peliculas).pack(pady=10)
            return
        
        # Crear un Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Título", "Director", "Duración", "Clasificación", "Género"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Título", text="Título")
        tree.heading("Director", text="Director")
        tree.heading("Duración", text="Duración")
        tree.heading("Clasificación", text="Clasificación")
        tree.heading("Género", text="Género")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Título", width=150)
        tree.column("Director", width=120)
        tree.column("Duración", width=80, anchor="center")
        tree.column("Clasificación", width=80, anchor="center")
        tree.column("Género", width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for pelicula in peliculas:
            tree.insert("", "end", values=(
                pelicula['id_pelicula'],
                pelicula['titulo'],
                pelicula['director'],
                f"{pelicula['duracion']} min",
                pelicula['clasificacion'],
                pelicula['genero']
            ))
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_peliculas).pack(pady=10)
    
    # Aquí continuarían los demás métodos adaptados a la interfaz gráfica...
    # Por razones de espacio, he mostrado cómo adaptar las principales funciones
    def editar_pelicula(self):
        """Interfaz para editar una película existente"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="EDITAR PELÍCULA", style='Header.TLabel').pack(pady=10)
        
        # Mostrar lista de películas
        self.cursor.execute("SELECT * FROM peliculas ORDER BY titulo")
        peliculas = self.cursor.fetchall()
        
        if not peliculas:
            ttk.Label(self.content_frame, text="No hay películas registradas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_peliculas).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione la película a editar:").pack()
        
        self.pelicula_var = tk.StringVar()
        pelicula_combobox = ttk.Combobox(self.content_frame, textvariable=self.pelicula_var, state="readonly")
        pelicula_combobox['values'] = [f"{p['id_pelicula']} - {p['titulo']}" for p in peliculas]
        pelicula_combobox.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Seleccionar", command=lambda: self.cargar_datos_edicion_pelicula(peliculas)).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_peliculas).pack(pady=5)
    
    def cargar_datos_edicion_pelicula(self, peliculas):
        """Carga los datos de la película seleccionada para edición"""
        seleccion = self.pelicula_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una película")
            return
        
        id_pelicula = int(seleccion.split(" - ")[0])
        pelicula = next((p for p in peliculas if p['id_pelicula'] == id_pelicula), None)
        
        if not pelicula:
            messagebox.showerror("Error", "Película no encontrada")
            return
        
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="EDITAR PELÍCULA", style='Header.TLabel').pack(pady=10)
        ttk.Label(self.content_frame, text=f"Editando: {pelicula['titulo']}").pack()
        
        # Campos de entrada con valores actuales
        fields = [
            ("Título:", "titulo_entry", pelicula['titulo']),
            ("Director:", "director_entry", pelicula['director']),
            ("Duración (minutos):", "duracion_entry", pelicula['duracion']),
            ("Clasificación:", "clasificacion_entry", pelicula['clasificacion']),
            ("Género:", "genero_entry", pelicula['genero'])
        ]
        
        self.entries = {}
        for text, name, value in fields:
            ttk.Label(self.content_frame, text=text).pack()
            entry = ttk.Entry(self.content_frame, width=30)
            entry.insert(0, value)
            entry.pack(pady=5)
            self.entries[name] = entry
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Guardar cambios", 
                  command=lambda: self.guardar_cambios_pelicula(id_pelicula)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.menu_gestion_peliculas).pack(side=tk.LEFT, padx=5)
    
    def guardar_cambios_pelicula(self, id_pelicula):
        """Guarda los cambios realizados a una película"""
        titulo = self.entries['titulo_entry'].get()
        director = self.entries['director_entry'].get()
        duracion = self.entries['duracion_entry'].get()
        clasificacion = self.entries['clasificacion_entry'].get()
        genero = self.entries['genero_entry'].get()
        
        # Validaciones
        if not titulo.strip():
            messagebox.showerror("Error", "El título no puede estar vacío.")
            return
        
        try:
            duracion = int(duracion)
            if duracion <= 0:
                messagebox.showerror("Error", "La duración debe ser mayor a 0 en minutos.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la duración.")
            return
        
        try:
            query = """
            UPDATE peliculas 
            SET titulo = %s, director = %s, duracion = %s, 
                clasificacion = %s, genero = %s
            WHERE id_pelicula = %s
            """
            self.cursor.execute(query, (titulo, director, duracion, clasificacion, genero, id_pelicula))
            self.conn.commit()
            messagebox.showinfo("Éxito", "¡Película actualizada exitosamente!")
            self.menu_gestion_peliculas()
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al actualizar película: {err}")

    def eliminar_pelicula(self):
        """Interfaz para eliminar una película"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="ELIMINAR PELÍCULA", style='Header.TLabel').pack(pady=10)
        
        # Mostrar lista de películas
        self.cursor.execute("SELECT * FROM peliculas ORDER BY titulo")
        peliculas = self.cursor.fetchall()
        
        if not peliculas:
            ttk.Label(self.content_frame, text="No hay películas registradas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_peliculas).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione la película a eliminar:").pack()
        
        self.pelicula_var = tk.StringVar()
        pelicula_combobox = ttk.Combobox(self.content_frame, textvariable=self.pelicula_var, state="readonly")
        pelicula_combobox['values'] = [f"{p['id_pelicula']} - {p['titulo']}" for p in peliculas]
        pelicula_combobox.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Eliminar", command=lambda: self.confirmar_eliminar_pelicula(peliculas)).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_peliculas).pack(pady=5)
    
    def confirmar_eliminar_pelicula(self, peliculas):
        """Confirma la eliminación de una película"""
        seleccion = self.pelicula_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una película")
            return
        
        id_pelicula = int(seleccion.split(" - ")[0])
        pelicula = next((p for p in peliculas if p['id_pelicula'] == id_pelicula), None)
        
        if not pelicula:
            messagebox.showerror("Error", "Película no encontrada")
            return
        
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Está seguro de eliminar la película '{pelicula['titulo']}'?\nEsta acción no se puede deshacer."
        )
        
        if confirmacion:
            try:
                # Primero eliminamos las funciones relacionadas
                self.cursor.execute("DELETE FROM funciones WHERE id_pelicula = %s", (id_pelicula,))
                
                # Luego eliminamos la película
                self.cursor.execute("DELETE FROM peliculas WHERE id_pelicula = %s", (id_pelicula,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "¡Película eliminada exitosamente!")
                self.menu_gestion_peliculas()
            except mysql.connector.Error as err:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al eliminar película: {err}")

    def buscar_pelicula(self):
        """Interfaz para buscar películas"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="BUSCAR PELÍCULA", style='Header.TLabel').pack(pady=10)
        
        ttk.Label(self.content_frame, text="Ingrese término de búsqueda (título o género):").pack()
        
        self.busqueda_entry = ttk.Entry(self.content_frame, width=30)
        self.busqueda_entry.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Buscar", command=self.ejecutar_busqueda_pelicula).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_peliculas).pack(pady=5)
        
        # Frame para resultados
        self.resultados_frame = ttk.Frame(self.content_frame)
        self.resultados_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def ejecutar_busqueda_pelicula(self):
        """Ejecuta la búsqueda de películas y muestra resultados"""
        termino = self.busqueda_entry.get().strip()
        
        if not termino:
            messagebox.showerror("Error", "Ingrese un término de búsqueda")
            return
        
        # Limpiar frame de resultados
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()
        
        query = """
        SELECT * FROM peliculas 
        WHERE titulo LIKE %s OR genero LIKE %s
        ORDER BY titulo
        """
        self.cursor.execute(query, (f"%{termino}%", f"%{termino}%"))
        peliculas = self.cursor.fetchall()
        
        if not peliculas:
            ttk.Label(self.resultados_frame, text="No se encontraron películas con ese criterio.").pack()
            return
        
        # Crear Treeview para mostrar resultados
        tree = ttk.Treeview(self.resultados_frame, columns=("ID", "Título", "Director", "Duración", "Clasificación", "Género"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Título", text="Título")
        tree.heading("Director", text="Director")
        tree.heading("Duración", text="Duración")
        tree.heading("Clasificación", text="Clasificación")
        tree.heading("Género", text="Género")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Título", width=150)
        tree.column("Director", width=120)
        tree.column("Duración", width=80, anchor="center")
        tree.column("Clasificación", width=80, anchor="center")
        tree.column("Género", width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(self.resultados_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for pelicula in peliculas:
            tree.insert("", "end", values=(
                pelicula['id_pelicula'],
                pelicula['titulo'],
                pelicula['director'],
                f"{pelicula['duracion']} min",
                pelicula['clasificacion'],
                pelicula['genero']
            ))

    def menu_gestion_salas(self):
        """Submenú para gestión de salas"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="GESTIÓN DE SALAS", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar sala", self.agregar_sala),
            ("Editar sala", self.editar_sala),
            ("Eliminar sala", self.eliminar_sala),
            ("Ver todas las salas", self.mostrar_todas_salas),
            ("Cambiar estado de sala", self.cambiar_estado_sala),
            ("Regresar", self.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=25).pack(pady=5)

    def agregar_sala(self):
        """Interfaz para agregar una nueva sala"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="AGREGAR SALA", style='Header.TLabel').pack(pady=10)
        
        # Campos de entrada
        fields = [
            ("Nombre de la sala:", "nombre_entry"),
            ("Capacidad de asientos:", "capacidad_entry")
        ]
        
        self.entries = {}
        for text, name in fields:
            ttk.Label(self.content_frame, text=text).pack()
            entry = ttk.Entry(self.content_frame, width=30)
            entry.pack(pady=5)
            self.entries[name] = entry
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Guardar", command=self.guardar_sala).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.menu_gestion_salas).pack(side=tk.LEFT, padx=5)
    
    def guardar_sala(self):
        """Guarda una nueva sala en la base de datos"""
        nombre = self.entries['nombre_entry'].get()
        capacidad = self.entries['capacidad_entry'].get()
        
        # Validaciones
        if not nombre.strip():
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return
        
        try:
            capacidad = int(capacidad)
            if capacidad <= 0:
                messagebox.showerror("Error", "La capacidad debe ser mayor a 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la capacidad.")
            return
        
        try:
            query = "INSERT INTO salas (nombre, capacidad) VALUES (%s, %s)"
            self.cursor.execute(query, (nombre, capacidad))
            self.conn.commit()
            messagebox.showinfo("Éxito", f"¡Sala '{nombre}' agregada exitosamente!")
            self.menu_gestion_salas()
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al agregar sala: {err}")

    def mostrar_todas_salas(self):
        """Muestra todas las salas del cine"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="LISTA DE SALAS", style='Header.TLabel').pack(pady=10)
        
        self.cursor.execute("SELECT * FROM salas ORDER BY nombre")
        salas = self.cursor.fetchall()
        
        if not salas:
            ttk.Label(self.content_frame, text="No hay salas registradas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=10)
            return
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Capacidad", "Estado"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Capacidad", text="Capacidad")
        tree.heading("Estado", text="Estado")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Nombre", width=150)
        tree.column("Capacidad", width=80, anchor="center")
        tree.column("Estado", width=120, anchor="center")
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for sala in salas:
            estado = "🟢 Disponible" if sala['estado'] == 'disponible' else "🔴 Mantenimiento"
            tree.insert("", "end", values=(
                sala['id_sala'],
                sala['nombre'],
                sala['capacidad'],
                estado
            ))
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=10)

    def editar_sala(self):
        """Interfaz para editar una sala existente"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="EDITAR SALA", style='Header.TLabel').pack(pady=10)
        
        # Mostrar lista de salas
        self.cursor.execute("SELECT * FROM salas ORDER BY nombre")
        salas = self.cursor.fetchall()
        
        if not salas:
            ttk.Label(self.content_frame, text="No hay salas registradas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione la sala a editar:").pack()
        
        self.sala_var = tk.StringVar()
        sala_combobox = ttk.Combobox(self.content_frame, textvariable=self.sala_var, state="readonly")
        sala_combobox['values'] = [f"{s['id_sala']} - {s['nombre']}" for s in salas]
        sala_combobox.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Seleccionar", command=lambda: self.cargar_datos_edicion_sala(salas)).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=5)
    
    def cargar_datos_edicion_sala(self, salas):
        """Carga los datos de la sala seleccionada para edición"""
        seleccion = self.sala_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una sala")
            return
        
        id_sala = int(seleccion.split(" - ")[0])
        sala = next((s for s in salas if s['id_sala'] == id_sala), None)
        
        if not sala:
            messagebox.showerror("Error", "Sala no encontrada")
            return
        
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="EDITAR SALA", style='Header.TLabel').pack(pady=10)
        ttk.Label(self.content_frame, text=f"Editando: {sala['nombre']}").pack()
        
        # Campos de entrada con valores actuales
        fields = [
            ("Nombre:", "nombre_entry", sala['nombre']),
            ("Capacidad:", "capacidad_entry", sala['capacidad'])
        ]
        
        self.entries = {}
        for text, name, value in fields:
            ttk.Label(self.content_frame, text=text).pack()
            entry = ttk.Entry(self.content_frame, width=30)
            entry.insert(0, value)
            entry.pack(pady=5)
            self.entries[name] = entry
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Guardar cambios", 
                  command=lambda: self.guardar_cambios_sala(id_sala)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.menu_gestion_salas).pack(side=tk.LEFT, padx=5)
    
    def guardar_cambios_sala(self, id_sala):
        """Guarda los cambios realizados a una sala"""
        nombre = self.entries['nombre_entry'].get()
        capacidad = self.entries['capacidad_entry'].get()
        
        # Validaciones
        if not nombre.strip():
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return
        
        try:
            capacidad = int(capacidad)
            if capacidad <= 0:
                messagebox.showerror("Error", "La capacidad debe ser mayor a 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la capacidad.")
            return
        
        try:
            query = "UPDATE salas SET nombre = %s, capacidad = %s WHERE id_sala = %s"
            self.cursor.execute(query, (nombre, capacidad, id_sala))
            self.conn.commit()
            messagebox.showinfo("Éxito", "¡Sala actualizada exitosamente!")
            self.menu_gestion_salas()
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al actualizar sala: {err}")

    def eliminar_sala(self):
        """Interfaz para eliminar una sala"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="ELIMINAR SALA", style='Header.TLabel').pack(pady=10)
        
        # Mostrar lista de salas
        self.cursor.execute("SELECT * FROM salas ORDER BY nombre")
        salas = self.cursor.fetchall()
        
        if not salas:
            ttk.Label(self.content_frame, text="No hay salas registradas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione la sala a eliminar:").pack()
        
        self.sala_var = tk.StringVar()
        sala_combobox = ttk.Combobox(self.content_frame, textvariable=self.sala_var, state="readonly")
        sala_combobox['values'] = [f"{s['id_sala']} - {s['nombre']}" for s in salas]
        sala_combobox.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Eliminar", command=lambda: self.confirmar_eliminar_sala(salas)).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=5)
    
    def confirmar_eliminar_sala(self, salas):
        """Confirma la eliminación de una sala"""
        seleccion = self.sala_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una sala")
            return
        
        id_sala = int(seleccion.split(" - ")[0])
        sala = next((s for s in salas if s['id_sala'] == id_sala), None)
        
        if not sala:
            messagebox.showerror("Error", "Sala no encontrada")
            return
        
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Está seguro de eliminar la sala '{sala['nombre']}'?\nEsta acción eliminará también todas sus funciones."
        )
        
        if confirmacion:
            try:
                # Primero eliminamos las funciones relacionadas
                self.cursor.execute("DELETE FROM funciones WHERE id_sala = %s", (id_sala,))
                
                # Luego eliminamos la sala
                self.cursor.execute("DELETE FROM salas WHERE id_sala = %s", (id_sala,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "¡Sala eliminada exitosamente!")
                self.menu_gestion_salas()
            except mysql.connector.Error as err:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al eliminar sala: {err}")

    def cambiar_estado_sala(self):
        """Interfaz para cambiar el estado de una sala"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="CAMBIAR ESTADO DE SALA", style='Header.TLabel').pack(pady=10)
        
        # Mostrar lista de salas
        self.cursor.execute("SELECT * FROM salas ORDER BY nombre")
        salas = self.cursor.fetchall()
        
        if not salas:
            ttk.Label(self.content_frame, text="No hay salas registradas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione la sala:").pack()
        
        self.sala_var = tk.StringVar()
        sala_combobox = ttk.Combobox(self.content_frame, textvariable=self.sala_var, state="readonly")
        sala_combobox['values'] = [f"{s['id_sala']} - {s['nombre']} ({'Disponible' if s['estado'] == 'disponible' else 'Mantenimiento'})" for s in salas]
        sala_combobox.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Cambiar estado", command=lambda: self.procesar_cambio_estado(salas)).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_salas).pack(pady=5)
    
    def procesar_cambio_estado(self, salas):
        """Procesa el cambio de estado de una sala"""
        seleccion = self.sala_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una sala")
            return
        
        id_sala = int(seleccion.split(" - ")[0])
        sala = next((s for s in salas if s['id_sala'] == id_sala), None)
        
        if not sala:
            messagebox.showerror("Error", "Sala no encontrada")
            return
        
        nuevo_estado = "mantenimiento" if sala['estado'] == "disponible" else "disponible"
        estado_texto = "Mantenimiento" if nuevo_estado == "mantenimiento" else "Disponible"
        
        confirmacion = messagebox.askyesno(
            "Confirmar cambio", 
            f"¿Cambiar estado de '{sala['nombre']}' a '{estado_texto}'?"
        )
        
        if confirmacion:
            try:
                query = "UPDATE salas SET estado = %s WHERE id_sala = %s"
                self.cursor.execute(query, (nuevo_estado, id_sala))
                self.conn.commit()
                
                estado_emoji = "🔴" if nuevo_estado == "mantenimiento" else "🟢"
                messagebox.showinfo("Éxito", f"¡Estado actualizado! {estado_emoji} Sala ahora en {nuevo_estado}")
                self.menu_gestion_salas()
            except mysql.connector.Error as err:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al actualizar estado: {err}")

    def menu_gestion_funciones(self):
        """Submenú para gestión de funciones"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="GESTIÓN DE FUNCIONES", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar función", self.agregar_funcion),
            ("Editar función", self.editar_funcion),
            ("Eliminar función", self.eliminar_funcion),
            ("Ver todas las funciones", self.mostrar_todas_funciones),
            ("Generar asientos para función", self.generar_asientos_funcion),
            ("Regresar", self.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=25).pack(pady=5)

    def agregar_funcion(self):
        """Interfaz para agregar una nueva función"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="AGREGAR FUNCIÓN", style='Header.TLabel').pack(pady=10)
        
        # Obtener películas disponibles
        self.cursor.execute("SELECT id_pelicula, titulo FROM peliculas ORDER BY titulo")
        peliculas = self.cursor.fetchall()
        
        if not peliculas:
            messagebox.showerror("Error", "No hay películas registradas. Primero agregue películas.")
            self.menu_gestion_funciones()
            return
        
        # Obtener salas disponibles
        self.cursor.execute("SELECT id_sala, nombre FROM salas WHERE estado = 'disponible' ORDER BY nombre")
        salas = self.cursor.fetchall()
        
        if not salas:
            messagebox.showerror("Error", "No hay salas disponibles. Active alguna sala primero.")
            self.menu_gestion_funciones()
            return
        
        # Campos de entrada
        ttk.Label(self.content_frame, text="Película:").pack()
        self.pelicula_var = tk.StringVar()
        pelicula_combobox = ttk.Combobox(self.content_frame, textvariable=self.pelicula_var, state="readonly")
        pelicula_combobox['values'] = [f"{p['id_pelicula']} - {p['titulo']}" for p in peliculas]
        pelicula_combobox.pack(pady=5)
        
        ttk.Label(self.content_frame, text="Sala:").pack()
        self.sala_var = tk.StringVar()
        sala_combobox = ttk.Combobox(self.content_frame, textvariable=self.sala_var, state="readonly")
        sala_combobox['values'] = [f"{s['id_sala']} - {s['nombre']}" for s in salas]
        sala_combobox.pack(pady=5)
        
        ttk.Label(self.content_frame, text="Fecha y hora (YYYY-MM-DD HH:MM):").pack()
        self.fecha_hora_entry = ttk.Entry(self.content_frame, width=30)
        self.fecha_hora_entry.pack(pady=5)
        
        ttk.Label(self.content_frame, text="Precio del boleto:").pack()
        self.precio_entry = ttk.Entry(self.content_frame, width=30)
        self.precio_entry.pack(pady=5)
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Guardar", command=lambda: self.guardar_funcion(peliculas, salas)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.menu_gestion_funciones).pack(side=tk.LEFT, padx=5)
    
    def guardar_funcion(self, peliculas, salas):
        """Guarda una nueva función en la base de datos"""
        pelicula_seleccionada = self.pelicula_var.get()
        sala_seleccionada = self.sala_var.get()
        fecha_hora = self.fecha_hora_entry.get()
        precio = self.precio_entry.get()
        
        # Validaciones
        if not pelicula_seleccionada:
            messagebox.showerror("Error", "Debe seleccionar una película")
            return
        
        if not sala_seleccionada:
            messagebox.showerror("Error", "Debe seleccionar una sala")
            return
        
        try:
            id_pelicula = int(pelicula_seleccionada.split(" - ")[0])
            id_sala = int(sala_seleccionada.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Selección no válida")
            return
        
        try:
            horario = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
            if horario <= datetime.now():
                messagebox.showerror("Error", "La función debe ser en el futuro.")
                return
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD HH:MM.")
            return
        
        try:
            precio = float(precio)
            if precio < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un precio válido.")
            return
        
        try:
            query = """
            INSERT INTO funciones (id_pelicula, id_sala, horario, precio)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (id_pelicula, id_sala, horario, precio))
            id_funcion = self.cursor.lastrowid
            self.conn.commit()
            
            # Preguntar si desea generar asientos
            if messagebox.askyesno("Generar asientos", "¿Desea generar los asientos para esta función?"):
                self.generar_asientos(id_funcion, id_sala)
            
            messagebox.showinfo("Éxito", "¡Función agregada exitosamente!")
            self.menu_gestion_funciones()
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al agregar función: {err}")
     
    def eliminar_funcion(self):
        """Elimina una función del sistema"""
        print("\n\033[1;36m" + " ELIMINAR FUNCIÓN " + "\033[0m")
        self.mostrar_todas_funciones()
        
        try:
            id_funcion = int(input("\nIngrese el ID de la función a eliminar: "))
        except ValueError:
            print("\033[91m" + "ID no válido." + "\033[0m")
            return
        
        # Verificar que la función existe
        query = """
        SELECT f.id_funcion, p.titulo, f.horario, s.nombre as sala_nombre
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        WHERE f.id_funcion = %s
        """
        self.cursor.execute(query, (id_funcion,))
        funcion = self.cursor.fetchone()
        
        if not funcion:
            print("\033[91m" + "No se encontró la función con ese ID." + "\033[0m")
            return
        
        confirmacion = input(
            f"¿Está seguro de eliminar la función de '{funcion['titulo']}' "
            f"el {funcion['horario'].strftime('%d/%m/%Y %H:%M')} en {funcion['sala_nombre']}? (s/n): "
        ).lower()
        
        if confirmacion != 's':
            print("\033[93m" + "Eliminación cancelada." + "\033[0m")
            return
        
        try:
            # Primero eliminamos los asientos relacionados
            self.cursor.execute("DELETE FROM asientos WHERE id_funcion = %s", (id_funcion,))
            
            # Luego eliminamos la función
            self.cursor.execute("DELETE FROM funciones WHERE id_funcion = %s", (id_funcion,))
            self.conn.commit()
            print("\033[92m" + "¡Función eliminada exitosamente!" + "\033[0m")
        except mysql.connector.Error as err:
            self.conn.rollback()
            print("\033[91m" + f"Error al eliminar función: {err}" + "\033[0m")        

    def generar_asientos(self, id_funcion, id_sala):
        """Genera los asientos para una función"""
        try:
            # Obtener capacidad de la sala
            self.cursor.execute("SELECT capacidad FROM salas WHERE id_sala = %s", (id_sala,))
            capacidad = self.cursor.fetchone()['capacidad']
            
            # Generar asientos (ejemplo: A1, A2, ..., B1, B2, ...)
            filas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            asientos_por_fila = (capacidad // len(filas)) + 1
            
            for fila in filas:
                for numero in range(1, asientos_por_fila + 1):
                    if len(filas) * (numero - 1) + filas.index(fila) + 1 > capacidad:
                        break
                    
                    numero_asiento = f"{fila}{numero}"
                    query = """
                    INSERT INTO asientos (id_funcion, numero_asiento, estado)
                    VALUES (%s, %s, 'disponible')
                    """
                    self.cursor.execute(query, (id_funcion, numero_asiento))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", f"Asientos generados: {capacidad}")
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al generar asientos: {err}")
    
    def editar_funcion(self):
        """Edita los datos de una función existente"""
        print("\n\033[1;36m" + " EDITAR FUNCIÓN " + "\033[0m")
        self.mostrar_todas_funciones()
        
        try:
            id_funcion = int(input("\nIngrese el ID de la función a editar: "))
        except ValueError:
            print("\033[91m" + "ID no válido." + "\033[0m")
            return
        
        # Verificar que la función existe
        query = """
        SELECT f.*, p.titulo, s.nombre as sala_nombre
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        WHERE f.id_funcion = %s
        """
        self.cursor.execute(query, (id_funcion,))
        funcion = self.cursor.fetchone()
        
        if not funcion:
            print("\033[91m" + "No se encontró la función con ese ID." + "\033[0m")
            return
        
        print("\nDeje en blanco los campos que no desea modificar:")
        
        # Mostrar películas disponibles
        self.cursor.execute("SELECT id_pelicula, titulo FROM peliculas ORDER BY titulo")
        peliculas = self.cursor.fetchall()
        print("\nPelículas disponibles:")
        for pelicula in peliculas:
            print(f"{pelicula['id_pelicula']}. {pelicula['titulo']}")
        
        id_pelicula_input = input(f"\nNuevo ID de película [{funcion['id_pelicula']} - {funcion['titulo']}]: ")
        id_pelicula = int(id_pelicula_input) if id_pelicula_input else funcion['id_pelicula']
        
        # Mostrar salas disponibles
        self.cursor.execute("SELECT id_sala, nombre FROM salas WHERE estado = 'disponible' ORDER BY nombre")
        salas = self.cursor.fetchall()
        print("\nSalas disponibles:")
        for sala in salas:
            print(f"{sala['id_sala']}. {sala['nombre']}")
        
        id_sala_input = input(f"\nNuevo ID de sala [{funcion['id_sala']} - {funcion['sala_nombre']}]: ")
        id_sala = int(id_sala_input) if id_sala_input else funcion['id_sala']
        
        # Validar fecha y hora
        while True:
            fecha_hora_input = input(f"Nueva fecha y hora [{funcion['horario'].strftime('%Y-%m-%d %H:%M')}]: ")
            if not fecha_hora_input:
                horario = funcion['horario']
                break
            try:
                horario = datetime.strptime(fecha_hora_input, "%Y-%m-%d %H:%M")
                if horario > datetime.now():
                    break
                print("\033[91m" + "La función debe ser en el futuro." + "\033[0m")
            except ValueError:
                print("\033[91m" + "Formato incorrecto. Use YYYY-MM-DD HH:MM." + "\033[0m")
        
        # Validar precio
        while True:
            precio_input = input(f"Nuevo precio [{funcion['precio']}]: ")
            if not precio_input:
                precio = funcion['precio']
                break
            try:
                precio = float(precio_input)
                if precio >= 0:
                    break
                print("\033[91m" + "El precio no puede ser negativo." + "\033[0m")
            except ValueError:
                print("\033[91m" + "Ingrese un número válido." + "\033[0m")
        
        try:
            query = """
            UPDATE funciones 
            SET id_pelicula = %s, id_sala = %s, horario = %s, precio = %s
            WHERE id_funcion = %s
            """
            self.cursor.execute(query, (id_pelicula, id_sala, horario, precio, id_funcion))
            self.conn.commit()
            print("\033[92m" + "¡Función actualizada exitosamente!" + "\033[0m")
        except mysql.connector.Error as err:
            self.conn.rollback()
            print("\033[91m" + f"Error al actualizar función: {err}" + "\033[0m")        

    def mostrar_todas_funciones(self):
        """Muestra todas las funciones programadas"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="LISTA DE FUNCIONES", style='Header.TLabel').pack(pady=10)
        
        query = """
        SELECT f.id_funcion, p.titulo, s.nombre as sala, 
               f.horario, f.precio, COUNT(a.id_asiento) as asientos_disponibles
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
        WHERE f.horario > NOW()
        GROUP BY f.id_funcion
        ORDER BY f.horario
        """
        
        self.cursor.execute(query)
        funciones = self.cursor.fetchall()
        
        if not funciones:
            ttk.Label(self.content_frame, text="No hay funciones programadas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_funciones).pack(pady=10)
            return
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Película", "Sala", "Horario", "Precio", "Asientos Disp."), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Película", text="Película")
        tree.heading("Sala", text="Sala")
        tree.heading("Horario", text="Horario")
        tree.heading("Precio", text="Precio")
        tree.heading("Asientos Disp.", text="Asientos Disp.")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Película", width=150)
        tree.column("Sala", width=100)
        tree.column("Horario", width=120)
        tree.column("Precio", width=80, anchor="center")
        tree.column("Asientos Disp.", width=80, anchor="center")
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for funcion in funciones:
            tree.insert("", "end", values=(
                funcion['id_funcion'],
                funcion['titulo'],
                funcion['sala'],
                funcion['horario'].strftime('%d/%m/%Y %H:%M'),
                f"${funcion['precio']:.2f}",
                funcion['asientos_disponibles']
            ))
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_funciones).pack(pady=10)

    def generar_asientos_funcion(self):
        """Interfaz para generar asientos para una función"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="GENERAR ASIENTOS PARA FUNCIÓN", style='Header.TLabel').pack(pady=10)
        
        # Obtener funciones sin asientos o que necesiten regeneración
        query = """
        SELECT f.id_funcion, p.titulo, s.nombre as sala, f.horario, 
               COUNT(a.id_asiento) as num_asientos, s.capacidad
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        LEFT JOIN asientos a ON f.id_funcion = a.id_funcion
        WHERE f.horario > NOW()
        GROUP BY f.id_funcion
        ORDER BY f.horario
        """
        
        self.cursor.execute(query)
        funciones = self.cursor.fetchall()
        
        if not funciones:
            ttk.Label(self.content_frame, text="No hay funciones programadas.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_funciones).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione la función:").pack()
        
        self.funcion_var = tk.StringVar()
        funcion_combobox = ttk.Combobox(self.content_frame, textvariable=self.funcion_var, state="readonly")
        funcion_combobox['values'] = [
            f"{f['id_funcion']} - {f['titulo']} ({f['horario'].strftime('%d/%m/%Y %H:%M')}) - Asientos: {f['num_asientos']}/{f['capacidad']}"
            for f in funciones
        ]
        funcion_combobox.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Generar asientos", 
                  command=lambda: self.confirmar_generar_asientos(funciones)).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_funciones).pack(pady=5)
    
    def confirmar_generar_asientos(self, funciones):
        """Confirma la generación de asientos para una función"""
        seleccion = self.funcion_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una función")
            return
        
        id_funcion = int(seleccion.split(" - ")[0])
        funcion = next((f for f in funciones if f['id_funcion'] == id_funcion), None)
        
        if not funcion:
            messagebox.showerror("Error", "Función no encontrada")
            return
        
        if funcion['num_asientos'] > 0:
            confirmacion = messagebox.askyesno(
                "Confirmar", 
                f"Esta función ya tiene {funcion['num_asientos']} asientos. ¿Desea eliminarlos y generar nuevos?"
            )
            if not confirmacion:
                return
            
            try:
                self.cursor.execute("DELETE FROM asientos WHERE id_funcion = %s", (id_funcion,))
            except mysql.connector.Error as err:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al eliminar asientos: {err}")
                return
        
        # Generar los nuevos asientos
        self.generar_asientos(id_funcion, funcion['id_sala'])
        messagebox.showinfo("Éxito", f"Asientos generados para la función: {funcion['titulo']}")
        self.menu_gestion_funciones()

    def menu_gestion_productos(self):
        """Submenú para gestión de productos del inventario"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="GESTIÓN DE PRODUCTOS", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Agregar producto", self.agregar_producto),
            ("Editar producto", self.editar_producto),
            ("Eliminar producto", self.eliminar_producto),
            ("Ver todos los productos", self.mostrar_todos_productos),
            ("Registrar entrada/salida", self.registrar_movimiento_inventario),
            ("Ver movimientos", self.mostrar_movimientos_inventario),
            ("Regresar", self.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=25).pack(pady=5)
       
    def agregar_producto(self):
        """Agrega un nuevo producto al inventario"""
        print("\n\033[1;36m" + " AGREGAR PRODUCTO " + "\033[0m")
        
        while True:
            nombre = input("Nombre del producto: ")
            if nombre.strip():
                break
            print("\033[91m" + "El nombre no puede estar vacío." + "\033[0m")
        
        while True:
            try:
                precio = float(input("Precio unitario: "))
                if precio >= 0:
                    break
                print("\033[91m" + "El precio no puede ser negativo." + "\033[0m")
            except ValueError:
                print("\033[91m" + "Ingrese un número válido." + "\033[0m")
        
        while True:
            try:
                stock = int(input("Stock inicial: "))
                if stock >= 0:
                    break
                print("\033[91m" + "El stock no puede ser negativo." + "\033[0m")
            except ValueError:
                print("\033[91m" + "Ingrese un número válido." + "\033[0m")
        
        try:
            query = """
            INSERT INTO productos (nombre, precio, stock)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (nombre, precio, stock))
            self.conn.commit()
            print("\033[92m" + f"¡Producto '{nombre}' agregado exitosamente!" + "\033[0m")
        except mysql.connector.Error as err:
            self.conn.rollback()
            print("\033[91m" + f"Error al agregar producto: {err}" + "\033[0m")

    def editar_producto(self):
        """Edita los datos de un producto existente"""
        print("\n\033[1;36m" + " EDITAR PRODUCTO " + "\033[0m")
        self.mostrar_todos_productos()
        
        try:
            id_producto = int(input("\nIngrese el ID del producto a editar: "))
        except ValueError:
            print("\033[91m" + "ID no válido." + "\033[0m")
            return
        
        # Verificar que el producto existe
        self.cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
        producto = self.cursor.fetchone()
        
        if not producto:
            print("\033[91m" + "No se encontró el producto con ese ID." + "\033[0m")
            return
        
        print("\nDeje en blanco los campos que no desea modificar:")
        nombre = input(f"Nuevo nombre [{producto['nombre']}]: ") or producto['nombre']
        
        while True:
            precio_input = input(f"Nuevo precio [{producto['precio']}]: ")
            if not precio_input:
                precio = producto['precio']
                break
            try:
                precio = float(precio_input)
                if precio >= 0:
                    break
                print("\033[91m" + "El precio no puede ser negativo." + "\033[0m")
            except ValueError:
                print("\033[91m" + "Ingrese un número válido." + "\033[0m")
        
        try:
            query = """
            UPDATE productos 
            SET nombre = %s, precio = %s
            WHERE id_producto = %s
            """
            self.cursor.execute(query, (nombre, precio, id_producto))
            self.conn.commit()
            print("\033[92m" + "¡Producto actualizado exitosamente!" + "\033[0m")
        except mysql.connector.Error as err:
            self.conn.rollback()
            print("\033[91m" + f"Error al actualizar producto: {err}" + "\033[0m")

    def eliminar_producto(self):
        """Elimina un producto del inventario"""
        print("\n\033[1;36m" + " ELIMINAR PRODUCTO " + "\033[0m")
        self.mostrar_todos_productos()
        
        try:
            id_producto = int(input("\nIngrese el ID del producto a eliminar: "))
        except ValueError:
            print("\033[91m" + "ID no válido." + "\033[0m")
            return
        
        # Verificar que el producto existe
        self.cursor.execute("SELECT nombre FROM productos WHERE id_producto = %s", (id_producto,))
        producto = self.cursor.fetchone()
        
        if not producto:
            print("\033[91m" + "No se encontró el producto con ese ID." + "\033[0m")
            return
        
        confirmacion = input(f"¿Está seguro de eliminar '{producto['nombre']}'? (s/n): ").lower()
        if confirmacion != 's':
            print("\033[93m" + "Eliminación cancelada." + "\033[0m")
            return
        
        try:
            # Primero eliminamos los movimientos relacionados
            self.cursor.execute("DELETE FROM movimientos_inventario WHERE id_producto = %s", (id_producto,))
            
            # Luego eliminamos el producto
            self.cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
            self.conn.commit()
            print("\033[92m" + "¡Producto eliminado exitosamente!" + "\033[0m")
        except mysql.connector.Error as err:
            self.conn.rollback()
            print("\033[91m" + f"Error al eliminar producto: {err}" + "\033[0m")        

    def mostrar_todos_productos(self):
        """Muestra todos los productos del inventario"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="LISTA DE PRODUCTOS", style='Header.TLabel').pack(pady=10)
        
        self.cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = self.cursor.fetchall()
        
        if not productos:
            ttk.Label(self.content_frame, text="No hay productos registrados.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_productos).pack(pady=10)
            return
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Precio", text="Precio")
        tree.heading("Stock", text="Stock")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Nombre", width=150)
        tree.column("Precio", width=80, anchor="center")
        tree.column("Stock", width=80, anchor="center")
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for producto in productos:
            stock = f"{producto['stock']} ✅" if producto['stock'] > 0 else f"{producto['stock']} ⚠️"
            tree.insert("", "end", values=(
                producto['id_producto'],
                producto['nombre'],
                f"${producto['precio']:.2f}",
                stock
            ))
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_productos).pack(pady=10)

    def registrar_movimiento_inventario(self):
        """Interfaz para registrar movimientos de inventario"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="MOVIMIENTO DE INVENTARIO", style='Header.TLabel').pack(pady=10)
        
        # Obtener lista de productos
        self.cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = self.cursor.fetchall()
        
        if not productos:
            ttk.Label(self.content_frame, text="No hay productos registrados.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_productos).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione el producto:").pack()
        
        self.producto_var = tk.StringVar()
        producto_combobox = ttk.Combobox(self.content_frame, textvariable=self.producto_var, state="readonly")
        producto_combobox['values'] = [f"{p['id_producto']} - {p['nombre']} (Stock: {p['stock']})" for p in productos]
        producto_combobox.pack(pady=10)
        
        # Tipo de movimiento
        ttk.Label(self.content_frame, text="Tipo de movimiento:").pack()
        
        self.tipo_movimiento = tk.StringVar(value="entrada")
        ttk.Radiobutton(self.content_frame, text="Entrada (aumentar stock)", variable=self.tipo_movimiento, value="entrada").pack()
        ttk.Radiobutton(self.content_frame, text="Salida (reducir stock)", variable=self.tipo_movimiento, value="salida").pack()
        
        # Cantidad
        ttk.Label(self.content_frame, text="Cantidad:").pack()
        self.cantidad_entry = ttk.Entry(self.content_frame, width=30)
        self.cantidad_entry.pack(pady=5)
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Registrar", 
                  command=lambda: self.procesar_movimiento(productos)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Regresar", 
                  command=self.menu_gestion_productos).pack(side=tk.LEFT, padx=5)
    
    def procesar_movimiento(self, productos):
        """Procesa el movimiento de inventario"""
        seleccion = self.producto_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar un producto")
            return
        
        id_producto = int(seleccion.split(" - ")[0])
        producto = next((p for p in productos if p['id_producto'] == id_producto), None)
        
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        
        try:
            cantidad = int(self.cantidad_entry.get())
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para la cantidad")
            return
        
        tipo = self.tipo_movimiento.get()
        
        if tipo == "salida" and cantidad > producto['stock']:
            messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {producto['stock']}")
            return
        
        try:
            # Registrar el movimiento
            query_movimiento = """
            INSERT INTO movimientos_inventario (id_producto, cantidad, tipo)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query_movimiento, (id_producto, cantidad, tipo))
            
            # Actualizar el stock
            if tipo == "entrada":
                query_stock = "UPDATE productos SET stock = stock + %s WHERE id_producto = %s"
            else:
                query_stock = "UPDATE productos SET stock = stock - %s WHERE id_producto = %s"
            
            self.cursor.execute(query_stock, (cantidad, id_producto))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "¡Movimiento registrado! Stock actualizado.")
            self.menu_gestion_productos()
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al registrar movimiento: {err}")

    def mostrar_movimientos_inventario(self):
        """Muestra el historial de movimientos de inventario"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="HISTORIAL DE INVENTARIO", style='Header.TLabel').pack(pady=10)
        
        query = """
        SELECT m.id_movimiento, p.nombre as producto, m.cantidad, m.tipo, m.fecha
        FROM movimientos_inventario m
        JOIN productos p ON m.id_producto = p.id_producto
        ORDER BY m.fecha DESC
        LIMIT 50
        """
        
        self.cursor.execute(query)
        movimientos = self.cursor.fetchall()
        
        if not movimientos:
            ttk.Label(self.content_frame, text="No hay movimientos registrados.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_productos).pack(pady=10)
            return
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Producto", "Cantidad", "Tipo", "Fecha"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Producto", text="Producto")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Fecha", text="Fecha")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Producto", width=150)
        tree.column("Cantidad", width=80, anchor="center")
        tree.column("Tipo", width=100, anchor="center")
        tree.column("Fecha", width=120)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for movimiento in movimientos:
            tipo = "⬆️ Entrada" if movimiento['tipo'] == 'entrada' else "⬇️ Salida"
            tree.insert("", "end", values=(
                movimiento['id_movimiento'],
                movimiento['producto'],
                movimiento['cantidad'],
                tipo,
                movimiento['fecha'].strftime('%d/%m/%Y %H:%M')
            ))
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", command=self.menu_gestion_productos).pack(pady=10)

    def mostrar_reportes(self):
        """Muestra diferentes reportes del sistema"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="REPORTES", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Ventas por película", self.reporte_ventas_pelicula),
            ("Asistencia por función", self.reporte_asistencia_funcion),
            ("Productos más vendidos", self.reporte_productos_vendidos),
            ("Ingresos totales", self.reporte_ingresos_totales),
            ("Regresar", self.mostrar_menu_administrador)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=25).pack(pady=5)

    def reporte_ventas_pelicula(self):
        """Muestra reporte de ventas por película"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="VENTAS POR PELÍCULA", style='Header.TLabel').pack(pady=10)
        
        # Obtener rango de fechas (últimos 30 días por defecto)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        ttk.Label(self.content_frame, 
                 text=f"Mostrando datos del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}").pack()
        
        query = """
        SELECT p.titulo, COUNT(b.id_boleto) as boletos_vendidos, 
               SUM(f.precio) as ingresos_totales
        FROM peliculas p
        JOIN funciones f ON p.id_pelicula = f.id_pelicula
        LEFT JOIN boletos b ON f.id_funcion = b.id_funcion
        WHERE f.horario BETWEEN %s AND %s
        GROUP BY p.id_pelicula
        ORDER BY ingresos_totales DESC
        """
        
        self.cursor.execute(query, (fecha_inicio, fecha_fin))
        resultados = self.cursor.fetchall()
        
        if not resultados:
            ttk.Label(self.content_frame, text="No hay datos de ventas en este período.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=self.mostrar_reportes).pack(pady=10)
            return
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("Película", "Boletos Vendidos", "Ingresos Totales"), show="headings")
        
        # Configurar columnas
        tree.heading("Película", text="Película")
        tree.heading("Boletos Vendidos", text="Boletos Vendidos")
        tree.heading("Ingresos Totales", text="Ingresos Totales")
        
        tree.column("Película", width=200)
        tree.column("Boletos Vendidos", width=120, anchor="center")
        tree.column("Ingresos Totales", width=120, anchor="center")
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        total_boletos = 0
        total_ingresos = 0.0
        
        for resultado in resultados:
            ingresos = resultado['ingresos_totales'] or 0
            tree.insert("", "end", values=(
                resultado['titulo'],
                resultado['boletos_vendidos'],
                f"${ingresos:.2f}"
            ))
            total_boletos += resultado['boletos_vendidos'] or 0
            total_ingresos += ingresos
        
        # Mostrar totales
        ttk.Label(self.content_frame, 
                 text=f"Total Boletos Vendidos: {total_boletos}").pack()
        ttk.Label(self.content_frame, 
                 text=f"Total Ingresos: ${total_ingresos:.2f}").pack()
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", command=self.mostrar_reportes).pack(pady=10)

    def comprar_boletos(self, usuario):
        """Interfaz para que un usuario compre boletos"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="COMPRA DE BOLETOS", style='Header.TLabel').pack(pady=10)
        
        # Obtener funciones disponibles
        query = """
        SELECT f.id_funcion, p.titulo, f.horario, s.nombre as sala, f.precio,
               COUNT(a.id_asiento) as asientos_disponibles
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        LEFT JOIN asientos a ON f.id_funcion = a.id_funcion AND a.estado = 'disponible'
        WHERE f.horario > NOW()
        GROUP BY f.id_funcion
        HAVING asientos_disponibles > 0
        ORDER BY f.horario
        """
        
        self.cursor.execute(query)
        funciones = self.cursor.fetchall()
        
        if not funciones:
            ttk.Label(self.content_frame, text="No hay funciones con asientos disponibles en este momento.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=lambda: self.mostrar_menu_usuario(usuario)).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione una función:").pack()
        
        self.funcion_var = tk.StringVar()
        funcion_combobox = ttk.Combobox(self.content_frame, textvariable=self.funcion_var, state="readonly")
        funcion_combobox['values'] = [f"{f['id_funcion']} - {f['titulo']} ({f['horario'].strftime('%d/%m/%Y %H:%M')})" for f in funciones]
        funcion_combobox.pack(pady=10)
        
        ttk.Button(self.content_frame, text="Continuar", 
                  command=lambda: self.seleccionar_asiento(usuario, funciones)).pack(pady=5)
        ttk.Button(self.content_frame, text="Regresar", 
                  command=lambda: self.mostrar_menu_usuario(usuario)).pack(pady=5)
    
    def seleccionar_asiento(self, usuario, funciones):
        """Interfaz para seleccionar asiento"""
        seleccion = self.funcion_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una función")
            return
        
        id_funcion = int(seleccion.split(" - ")[0])
        funcion = next((f for f in funciones if f['id_funcion'] == id_funcion), None)
        
        if not funcion:
            messagebox.showerror("Error", "Función no encontrada")
            return
        
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="SELECCIONAR ASIENTO", style='Header.TLabel').pack(pady=10)
        ttk.Label(self.content_frame, text=f"Película: {funcion['titulo']}").pack()
        ttk.Label(self.content_frame, text=f"Horario: {funcion['horario'].strftime('%d/%m/%Y %H:%M')}").pack()
        ttk.Label(self.content_frame, text=f"Sala: {funcion['sala']}").pack()
        ttk.Label(self.content_frame, text=f"Precio: ${funcion['precio']:.2f}").pack()
        
        # Obtener asientos disponibles
        query = """
        SELECT id_asiento, numero_asiento 
        FROM asientos 
        WHERE id_funcion = %s AND estado = 'disponible'
        ORDER BY numero_asiento
        """
        self.cursor.execute(query, (id_funcion,))
        asientos = self.cursor.fetchall()
        
        ttk.Label(self.content_frame, text="Asientos disponibles:").pack()
        
        self.asiento_var = tk.StringVar()
        asiento_combobox = ttk.Combobox(self.content_frame, textvariable=self.asiento_var, state="readonly")
        asiento_combobox['values'] = [a['numero_asiento'] for a in asientos]
        asiento_combobox.pack(pady=10)
        
        # Métodos de pago
        ttk.Label(self.content_frame, text="Método de pago:").pack()
        
        self.metodo_pago = tk.StringVar(value="tarjeta")
        metodos = [
            ("Tarjeta de crédito/débito", "tarjeta"),
            ("PayPal", "paypal"),
            ("Efectivo", "efectivo"),
            ("Criptomonedas", "cripto")
        ]
        
        for text, value in metodos:
            ttk.Radiobutton(self.content_frame, text=text, variable=self.metodo_pago, value=value).pack(anchor="w")
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Comprar", 
                  command=lambda: self.procesar_compra_boleto(usuario, funcion, asientos)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=lambda: self.mostrar_menu_usuario(usuario)).pack(side=tk.LEFT, padx=5)
    
    def procesar_compra_boleto(self, usuario, funcion, asientos):
        """Procesa la compra de un boleto"""
        numero_asiento = self.asiento_var.get()
        if not numero_asiento:
            messagebox.showerror("Error", "Debe seleccionar un asiento")
            return
        
        # Verificar si el asiento existe y está disponible
        asiento = next((a for a in asientos if a['numero_asiento'] == numero_asiento), None)
        
        if not asiento:
            messagebox.showerror("Error", "Asiento no disponible o no válido")
            return
        
        metodo_pago = self.metodo_pago.get()
        
        try:
            # Insertar boleto
            query_boleto = """
            INSERT INTO boletos (id_usuario, id_funcion, id_asiento)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query_boleto, (usuario['id_usuario'], funcion['id_funcion'], asiento['id_asiento']))
            
            # Actualizar estado del asiento
            query_asiento = """
            UPDATE asientos SET estado = 'ocupado' WHERE id_asiento = %s
            """
            self.cursor.execute(query_asiento, (asiento['id_asiento'],))
            
            # Registrar pago
            id_boleto = self.cursor.lastrowid
            query_pago = """
            INSERT INTO pagos (id_boleto, metodo, estado)
            VALUES (%s, %s, 'completado')
            """
            self.cursor.execute(query_pago, (id_boleto, metodo_pago))
            
            self.conn.commit()
            
            # Mostrar resumen de compra
            resumen = f"""
            ¡Compra exitosa! Disfrute de {funcion['titulo']}.
            
            Fecha: {funcion['horario'].strftime('%d/%m/%Y %H:%M')}
            Sala: {funcion['sala']}
            Asiento: {numero_asiento}
            Precio: ${funcion['precio']:.2f}
            Método de pago: {metodo_pago.capitalize()}
            """
            
            messagebox.showinfo("Éxito", resumen)
            self.mostrar_menu_usuario(usuario)
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al procesar la compra: {err}")

    def comprar_productos(self, usuario):
        """Interfaz para comprar productos del inventario"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="COMPRA DE PRODUCTOS", style='Header.TLabel').pack(pady=10)
        
        # Obtener productos disponibles
        self.cursor.execute("SELECT * FROM productos WHERE stock > 0 ORDER BY nombre")
        productos = self.cursor.fetchall()
        
        if not productos:
            ttk.Label(self.content_frame, text="No hay productos disponibles en este momento.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=lambda: self.mostrar_menu_usuario(usuario)).pack(pady=10)
            return
        
        # Crear lista de productos con Checkbuttons
        self.carrito = []
        self.productos_vars = []
        
        for producto in productos:
            var = tk.IntVar(value=0)
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Checkbutton(frame, text=f"{producto['nombre']} (${producto['precio']:.2f} - Stock: {producto['stock']})", 
                          variable=var, 
                          command=lambda p=producto, v=var: self.actualizar_carrito(p, v)).pack(side=tk.LEFT)
            
            spinbox = ttk.Spinbox(frame, from_=1, to=producto['stock'], width=5)
            spinbox.pack(side=tk.LEFT, padx=5)
            self.productos_vars.append((var, spinbox, producto))
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Ver carrito", command=self.mostrar_carrito).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Regresar", command=lambda: self.mostrar_menu_usuario(usuario)).pack(side=tk.LEFT, padx=5)
    
    def actualizar_carrito(self, producto, var):
        """Actualiza el carrito de compras"""
        if var.get() == 1:
            if producto not in [item['producto'] for item in self.carrito]:
                self.carrito.append({
                    'producto': producto,
                    'cantidad': 1
                })
        else:
            self.carrito = [item for item in self.carrito if item['producto']['id_producto'] != producto['id_producto']]
    
    def mostrar_carrito(self):
        """Muestra el contenido del carrito de compras"""
        if not self.carrito:
            messagebox.showinfo("Carrito vacío", "No hay productos en el carrito")
            return
        
        # Actualizar cantidades en el carrito
        for item in self.carrito:
            for var, spinbox, producto in self.productos_vars:
                if producto['id_producto'] == item['producto']['id_producto']:
                    try:
                        cantidad = int(spinbox.get())
                        if 1 <= cantidad <= producto['stock']:
                            item['cantidad'] = cantidad
                        else:
                            messagebox.showerror("Error", f"Cantidad no válida para {producto['nombre']}")
                            return
                    except ValueError:
                        messagebox.showerror("Error", f"Ingrese una cantidad válida para {producto['nombre']}")
                        return
        
        # Mostrar resumen del carrito
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="RESUMEN DE COMPRA", style='Header.TLabel').pack(pady=10)
        
        total = 0.0
        
        for item in self.carrito:
            producto = item['producto']
            cantidad = item['cantidad']
            subtotal = producto['precio'] * cantidad
            total += subtotal
            
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"{producto['nombre']} x {cantidad}").pack(side=tk.LEFT)
            ttk.Label(frame, text=f"${subtotal:.2f}").pack(side=tk.RIGHT)
        
        ttk.Label(self.content_frame, text=f"TOTAL: ${total:.2f}", font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Confirmar compra", command=self.confirmar_compra_productos).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Seguir comprando", command=self.comprar_productos).pack(side=tk.LEFT, padx=5)
    
    def confirmar_compra_productos(self):
        """Confirma la compra de productos"""
        if not self.carrito:
            messagebox.showerror("Error", "No hay productos en el carrito")
            return
        
        try:
            for item in self.carrito:
                producto = item['producto']
                cantidad = item['cantidad']
                
                # Registrar movimiento de inventario (salida)
                query_movimiento = """
                INSERT INTO movimientos_inventario (id_producto, cantidad, tipo)
                VALUES (%s, %s, 'salida')
                """
                self.cursor.execute(query_movimiento, (producto['id_producto'], cantidad))
                
                # Actualizar stock
                query_stock = "UPDATE productos SET stock = stock - %s WHERE id_producto = %s"
                self.cursor.execute(query_stock, (cantidad, producto['id_producto']))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "¡Compra realizada con éxito! Gracias por su preferencia.")
            self.carrito = []
            self.mostrar_menu_usuario()
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al procesar la compra: {err}")

    def mostrar_boletos_usuario(self, id_usuario):
        """Muestra los boletos comprados por el usuario"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="MIS BOLETOS", style='Header.TLabel').pack(pady=10)
        
        query = """
        SELECT b.id_boleto, p.titulo, f.horario, s.nombre as sala, 
               a.numero_asiento, f.precio, b.fecha_compra
        FROM boletos b
        JOIN funciones f ON b.id_funcion = f.id_funcion
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        JOIN asientos a ON b.id_asiento = a.id_asiento
        WHERE b.id_usuario = %s AND f.horario > NOW()
        ORDER BY f.horario
        """
        
        self.cursor.execute(query, (id_usuario,))
        boletos = self.cursor.fetchall()
        
        if not boletos:
            ttk.Label(self.content_frame, text="No tienes boletos activos.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=lambda: self.mostrar_menu_usuario({'id_usuario': id_usuario})).pack(pady=10)
            return
        
        # Crear Treeview para mostrar la tabla
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Película", "Horario", "Sala", "Asiento", "Precio", "Fecha Compra"), show="headings")
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.heading("Película", text="Película")
        tree.heading("Horario", text="Horario")
        tree.heading("Sala", text="Sala")
        tree.heading("Asiento", text="Asiento")
        tree.heading("Precio", text="Precio")
        tree.heading("Fecha Compra", text="Fecha Compra")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Película", width=150)
        tree.column("Horario", width=120)
        tree.column("Sala", width=100)
        tree.column("Asiento", width=80, anchor="center")
        tree.column("Precio", width=80, anchor="center")
        tree.column("Fecha Compra", width=120)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for boleto in boletos:
            tree.insert("", "end", values=(
                boleto['id_boleto'],
                boleto['titulo'],
                boleto['horario'].strftime('%d/%m/%Y %H:%M'),
                boleto['sala'],
                boleto['numero_asiento'],
                f"${boleto['precio']:.2f}",
                boleto['fecha_compra'].strftime('%d/%m/%Y %H:%M')
            ))
        
        # Botón de regreso
        ttk.Button(self.content_frame, text="Regresar", 
                  command=lambda: self.mostrar_menu_usuario({'id_usuario': id_usuario})).pack(pady=10)

    def solicitar_devolucion(self, id_usuario):
        """Interfaz para solicitar devolución de un boleto"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text="SOLICITAR DEVOLUCIÓN", style='Header.TLabel').pack(pady=10)
        
        # Obtener boletos que pueden ser devueltos
        query = """
        SELECT b.id_boleto, p.titulo, f.horario, s.nombre as sala, 
               a.numero_asiento, f.precio
        FROM boletos b
        JOIN funciones f ON b.id_funcion = f.id_funcion
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        JOIN asientos a ON b.id_asiento = a.id_asiento
        WHERE b.id_usuario = %s AND f.horario > NOW()
        AND NOT EXISTS (
            SELECT 1 FROM devoluciones d 
            WHERE d.id_boleto = b.id_boleto AND d.estado != 'rechazada'
        )
        ORDER BY f.horario
        """
        
        self.cursor.execute(query, (id_usuario,))
        boletos = self.cursor.fetchall()
        
        if not boletos:
            ttk.Label(self.content_frame, text="No tienes boletos que puedan ser devueltos.").pack()
            ttk.Button(self.content_frame, text="Regresar", command=lambda: self.mostrar_menu_usuario({'id_usuario': id_usuario})).pack(pady=10)
            return
        
        ttk.Label(self.content_frame, text="Seleccione el boleto a devolver:").pack()
        
        self.boleto_var = tk.StringVar()
        boleto_combobox = ttk.Combobox(self.content_frame, textvariable=self.boleto_var, state="readonly")
        boleto_combobox['values'] = [f"{b['id_boleto']} - {b['titulo']} ({b['horario'].strftime('%d/%m/%Y %H:%M')})" for b in boletos]
        boleto_combobox.pack(pady=10)
        
        ttk.Label(self.content_frame, text="Motivo de la devolución:").pack()
        self.motivo_entry = tk.Text(self.content_frame, height=5, width=50)
        self.motivo_entry.pack(pady=10)
        
        # Botones
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Solicitar devolución", 
                  command=lambda: self.procesar_devolucion(id_usuario, boletos)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Regresar", 
                  command=lambda: self.mostrar_menu_usuario({'id_usuario': id_usuario})).pack(side=tk.LEFT, padx=5)
    
    def procesar_devolucion(self, id_usuario, boletos):
        """Procesa la solicitud de devolución"""
        seleccion = self.boleto_var.get()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar un boleto")
            return
        
        id_boleto = int(seleccion.split(" - ")[0])
        boleto = next((b for b in boletos if b['id_boleto'] == id_boleto), None)
        
        if not boleto:
            messagebox.showerror("Error", "Boleto no encontrado")
            return
        
        motivo = self.motivo_entry.get("1.0", tk.END).strip()
        if not motivo:
            messagebox.showerror("Error", "Debe ingresar un motivo para la devolución")
            return
        
        try:
            query = """
            INSERT INTO devoluciones (id_boleto, motivo, estado)
            VALUES (%s, %s, 'pendiente')
            """
            self.cursor.execute(query, (id_boleto, motivo))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Solicitud de devolución registrada. Será revisada por nuestro equipo.")
            self.mostrar_menu_usuario({'id_usuario': id_usuario})
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al solicitar devolución: {err}")
            
    def reporte_asistencia_funcion(self):
        """Muestra reporte de asistencia por función"""
        print("\n\033[1;34m" + " ASISTENCIA POR FUNCIÓN " + "\033[0m")
        
        query = """
        SELECT f.id_funcion, p.titulo, s.nombre as sala, f.horario,
               COUNT(b.id_boleto) as asistencia, 
               (COUNT(b.id_boleto) / s.capacidad * 100 as porcentaje_ocupacion
        FROM funciones f
        JOIN peliculas p ON f.id_pelicula = p.id_pelicula
        JOIN salas s ON f.id_sala = s.id_sala
        LEFT JOIN boletos b ON f.id_funcion = b.id_funcion
        WHERE f.horario BETWEEN %s AND %s
        GROUP BY f.id_funcion
        ORDER BY f.horario
        """
        
        # Obtener rango de fechas (últimos 7 días por defecto)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=7)
        
        print(f"\nMostrando datos del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}")
        
        self.cursor.execute(query, (fecha_inicio, fecha_fin))
        resultados = self.cursor.fetchall()
        
        if not resultados:
            print("\033[93m" + "No hay datos de funciones en este período." + "\033[0m")
            return
        
        tabla = PrettyTable()
        tabla.field_names = ["ID", "Película", "Sala", "Horario", "Asistencia", "Ocupación"]
        tabla.align = "l"
        
        for resultado in resultados:
            ocupacion = f"{resultado['porcentaje_ocupacion']:.1f}%"
            if resultado['porcentaje_ocupacion'] > 80:
                ocupacion = f"\033[92m{ocupacion}\033[0m"  # Verde si >80%
            elif resultado['porcentaje_ocupacion'] < 30:
                ocupacion = f"\033[91m{ocupacion}\033[0m"  # Rojo si <30%
            
            tabla.add_row([
                resultado['id_funcion'],
                resultado['titulo'],
                resultado['sala'],
                resultado['horario'].strftime('%d/%m/%Y %H:%M'),
                resultado['asistencia'],
                ocupacion
            ])
        
        print(tabla)

    def reporte_productos_vendidos(self):
        """Muestra reporte de productos más vendidos"""
        print("\n\033[1;34m" + " PRODUCTOS MÁS VENDIDOS " + "\033[0m")
        
        query = """
        SELECT p.nombre, SUM(m.cantidad) as cantidad_vendida,
               SUM(m.cantidad * p.precio) as ingresos_totales
        FROM productos p
        JOIN movimientos_inventario m ON p.id_producto = m.id_producto
        WHERE m.tipo = 'salida' AND m.fecha BETWEEN %s AND %s
        GROUP BY p.id_producto
        ORDER BY cantidad_vendida DESC
        LIMIT 10
        """
        
        # Obtener rango de fechas (últimos 30 días por defecto)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        print(f"\nMostrando datos del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}")
        
        self.cursor.execute(query, (fecha_inicio, fecha_fin))
        resultados = self.cursor.fetchall()
        
        if not resultados:
            print("\033[93m" + "No hay datos de ventas de productos en este período." + "\033[0m")
            return
        
        tabla = PrettyTable()
        tabla.field_names = ["Producto", "Cantidad Vendida", "Ingresos Totales"]
        tabla.align = "l"
        tabla.float_format = ".2"
        
        for resultado in resultados:
            tabla.add_row([
                resultado['nombre'],
                resultado['cantidad_vendida'],
                f"${resultado['ingresos_totales']:.2f}"
            ])
        
        print(tabla)

    def reporte_ingresos_totales(self):
        """Muestra reporte de ingresos totales"""
        print("\n\033[1;34m" + " INGRESOS TOTALES " + "\033[0m")
        
        # Ingresos por boletos
        query_boletos = """
        SELECT SUM(f.precio) as total
        FROM boletos b
        JOIN funciones f ON b.id_funcion = f.id_funcion
        WHERE b.fecha_compra BETWEEN %s AND %s
        """
        
        # Ingresos por productos
        query_productos = """
        SELECT SUM(m.cantidad * p.precio) as total
        FROM movimientos_inventario m
        JOIN productos p ON m.id_producto = p.id_producto
        WHERE m.tipo = 'salida' AND m.fecha BETWEEN %s AND %s
        """
        
        # Obtener rango de fechas (últimos 30 días por defecto)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        print(f"\nMostrando datos del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}")
        
        # Obtener ingresos por boletos
        self.cursor.execute(query_boletos, (fecha_inicio, fecha_fin))
        ingresos_boletos = self.cursor.fetchone()['total'] or 0
        
        # Obtener ingresos por productos
        self.cursor.execute(query_productos, (fecha_inicio, fecha_fin))
        ingresos_productos = self.cursor.fetchone()['total'] or 0
        
        total = ingresos_boletos + ingresos_productos
        
        tabla = PrettyTable()
        tabla.field_names = ["Concepto", "Ingresos"]
        tabla.align = "l"
        tabla.float_format = ".2"
        
        tabla.add_row(["Venta de Boletos", f"${ingresos_boletos:.2f}"])
        tabla.add_row(["Venta de Productos", f"${ingresos_productos:.2f}"])
        tabla.add_row(["", ""])
        tabla.add_row(["TOTAL", f"${total:.2f}"])
        
        print(tabla)        
    
    def mostrar_menu_usuario(self, usuario):
        """Muestra el menú para usuarios registrados"""
        self.limpiar_contenido()
        
        ttk.Label(self.content_frame, text=f"BIENVENIDO {usuario['nombre'].upper()}", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Ver cartelera", self.mostrar_cartelera),
            ("Comprar boletos", lambda: self.comprar_boletos(usuario)),
            ("Comprar productos", lambda: self.comprar_productos(usuario)),
            ("Ver mis boletos", lambda: self.mostrar_boletos_usuario(usuario['id_usuario'])),
            ("Solicitar devolución", lambda: self.solicitar_devolucion(usuario['id_usuario'])),
            ("Cerrar sesión", self.mostrar_menu_principal)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command, width=25).pack(pady=5)
    
    def salir(self):
        """Cierra la aplicación"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = CineManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()