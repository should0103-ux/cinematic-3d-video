extends Node3D

const ASSET_ROOT := "res://assets"

var elapsed := 0.0
var character: Node3D
var animation_player: AnimationPlayer
var ants: Array[Node3D] = []
var caption: Label3D
var camera: Camera3D

func _ready() -> void:
    _setup_environment()
    _setup_lab()
    _load_animated_character()
    _setup_ants()
    _setup_caption()
    print("GODOT_TEST_SCENE_READY")

func _setup_environment() -> void:
    var world := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.012, 0.045, 0.075, 1.0)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.50, 0.75, 0.90)
    env.ambient_light_energy = 0.48
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    world.environment = env
    add_child(world)

    camera = Camera3D.new()
    camera.position = Vector3(0.0, 2.55, 6.6)
    camera.fov = 38.0
    add_child(camera)
    camera.look_at(Vector3(0.0, 1.45, 0.0), Vector3.UP)
    camera.current = true

    var key := DirectionalLight3D.new()
    key.rotation_degrees = Vector3(-32.0, -28.0, 0.0)
    key.light_color = Color(0.66, 0.88, 1.0)
    key.light_energy = 0.82
    key.shadow_enabled = true
    add_child(key)

    var fill := OmniLight3D.new()
    fill.position = Vector3(-3.2, 3.0, 2.7)
    fill.light_color = Color(0.12, 0.72, 1.0)
    fill.light_energy = 0.82
    fill.omni_range = 9.0
    add_child(fill)

    var rim := OmniLight3D.new()
    rim.position = Vector3(3.0, 2.7, -2.5)
    rim.light_color = Color(0.08, 0.42, 0.95)
    rim.light_energy = 1.05
    rim.omni_range = 8.0
    add_child(rim)

func _setup_lab() -> void:
    var floor := MeshInstance3D.new()
    var floor_mesh := PlaneMesh.new()
    floor_mesh.size = Vector2(16.0, 16.0)
    floor.mesh = floor_mesh
    floor.position = Vector3(0.0, -0.04, 0.0)
    var floor_mat := StandardMaterial3D.new()
    floor_mat.albedo_color = Color(0.018, 0.10, 0.14)
    floor_mat.metallic = 0.35
    floor_mat.roughness = 0.28
    floor.set_surface_override_material(0, floor_mat)
    add_child(floor)

    var table := MeshInstance3D.new()
    var table_mesh := BoxMesh.new()
    table_mesh.size = Vector3(5.2, 0.22, 2.5)
    table.mesh = table_mesh
    table.position = Vector3(0.25, 0.94, 0.72)
    var table_mat := StandardMaterial3D.new()
    table_mat.albedo_color = Color(0.055, 0.14, 0.19)
    table_mat.metallic = 0.48
    table_mat.roughness = 0.24
    table.set_surface_override_material(0, table_mat)
    add_child(table)

    var dish := MeshInstance3D.new()
    var dish_mesh := CylinderMesh.new()
    dish_mesh.top_radius = 0.66
    dish_mesh.bottom_radius = 0.66
    dish_mesh.height = 0.075
    dish.mesh = dish_mesh
    dish.position = Vector3(0.72, 1.09, 0.56)
    var dish_mat := StandardMaterial3D.new()
    dish_mat.albedo_color = Color(0.30, 0.67, 0.76, 0.48)
    dish_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    dish_mat.metallic = 0.16
    dish_mat.roughness = 0.12
    dish.set_surface_override_material(0, dish_mat)
    add_child(dish)

    var yogurt := MeshInstance3D.new()
    var yogurt_mesh := CylinderMesh.new()
    yogurt_mesh.top_radius = 0.52
    yogurt_mesh.bottom_radius = 0.52
    yogurt_mesh.height = 0.035
    yogurt.mesh = yogurt_mesh
    yogurt.position = Vector3(0.72, 1.145, 0.56)
    var yogurt_mat := StandardMaterial3D.new()
    yogurt_mat.albedo_color = Color(0.91, 0.88, 0.76)
    yogurt_mat.roughness = 0.22
    yogurt_mat.metallic = 0.02
    yogurt.set_surface_override_material(0, yogurt_mat)
    add_child(yogurt)

    _add_glassware(Vector3(1.75, 1.10, 0.55), 0.18, 0.55)
    _add_glassware(Vector3(-1.95, 1.10, 0.35), 0.14, 0.42)

func _add_glassware(pos: Vector3, radius: float, height: float) -> void:
    var glass := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius
    mesh.bottom_radius = radius * 0.88
    mesh.height = height
    glass.mesh = mesh
    glass.position = pos + Vector3(0.0, height * 0.5, 0.0)
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color(0.22, 0.63, 0.72, 0.28)
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.roughness = 0.08
    mat.metallic = 0.16
    glass.set_surface_override_material(0, mat)
    add_child(glass)

func _collect_glbs(dir_path: String, results: Array[String]) -> void:
    var dir := DirAccess.open(dir_path)
    if dir == null:
        return
    dir.list_dir_begin()
    var entry := dir.get_next()
    while entry != "":
        if dir.current_is_dir():
            if not entry.begins_with("."):
                _collect_glbs(dir_path.path_join(entry), results)
        elif entry.to_lower().ends_with(".glb"):
            results.append(dir_path.path_join(entry))
        entry = dir.get_next()
    dir.list_dir_end()

func _load_animated_character() -> void:
    var paths: Array[String] = []
    _collect_glbs(ASSET_ROOT, paths)
    paths.sort()
    if paths.is_empty():
        push_error("No GLB assets were found under res://assets")
        return

    var chosen := paths[0]
    for path in paths:
        if "researcher" in path.to_lower():
            chosen = path
            break
    if not "researcher" in chosen.to_lower():
        for path in paths:
            var lower := path.to_lower()
            if "walk" in lower:
                chosen = path
                break
            if "idle" in lower:
                chosen = path

    print("Loading animated GLB: ", chosen)
    var packed := load(chosen) as PackedScene
    if packed == null:
        push_error("Could not import GLB as PackedScene: " + chosen)
        return

    character = packed.instantiate() as Node3D
    if character == null:
        push_error("GLB root is not Node3D: " + chosen)
        return
    character.position = Vector3(-0.82, 0.0, -0.72)
    character.scale = Vector3.ONE * 1.35
    add_child(character)

    if "researcher" in chosen.to_lower():
        print("Visible static researcher mesh loaded; animation pack import is separate")
        return

    var players := character.find_children("*", "AnimationPlayer", true, false)
    if players.is_empty():
        push_warning("No AnimationPlayer found inside imported GLB")
        return

    animation_player = players[0] as AnimationPlayer
    var clips := animation_player.get_animation_list()
    print("Imported animations: ", clips)
    if clips.is_empty():
        push_warning("Imported GLB has no animation clips")
        return

    var selected_clip := clips[0]
    for clip in clips:
        if "walk" in clip.to_lower() or "idle" in clip.to_lower():
            selected_clip = clip
            break
    animation_player.play(selected_clip)
    print("Playing animation: ", selected_clip)

func _make_ant() -> Node3D:
    var ant_scene := load("res://assets/ant.glb") as PackedScene
    if ant_scene != null:
        var real_ant := ant_scene.instantiate() as Node3D
        if real_ant != null:
            real_ant.scale = Vector3.ONE * 0.12
            return real_ant
    var ant := Node3D.new()
    var body_mat := StandardMaterial3D.new()
    body_mat.albedo_color = Color(0.16, 0.035, 0.018)
    body_mat.roughness = 0.42
    for item in [
        {"p": Vector3(0.0, 0.0, 0.0), "r": 0.040},
        {"p": Vector3(0.0, 0.0, 0.09), "r": 0.030},
        {"p": Vector3(0.0, 0.0, -0.075), "r": 0.045}
    ]:
        var part := MeshInstance3D.new()
        var sphere := SphereMesh.new()
        sphere.radius = item["r"]
        sphere.height = item["r"] * 2.0
        part.mesh = sphere
        part.position = item["p"]
        part.set_surface_override_material(0, body_mat)
        ant.add_child(part)
    return ant

func _setup_ants() -> void:
    for i in range(7):
        var ant := _make_ant()
        add_child(ant)
        ants.append(ant)

func _setup_caption() -> void:
    caption = Label3D.new()
    caption.text = "A STRANGE SCIENCE EXPERIMENT"
    caption.font_size = 48
    caption.pixel_size = 0.0019
    caption.modulate = Color(0.78, 0.94, 1.0, 0.96)
    caption.position = Vector3(0.0, 2.58, 0.22)
    caption.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    add_child(caption)

func _process(delta: float) -> void:
    elapsed += delta
    var shot_position := Vector3(0.0, 2.55, 6.6)
    var shot_target := Vector3(0.0, 1.45, 0.0)
    if elapsed < 6.0:
        caption.text = "A STRANGE SCIENCE EXPERIMENT"
        shot_position = Vector3(0.0, 2.55, 6.6)
        shot_target = Vector3(0.0, 1.45, 0.0)
    elif elapsed < 12.0:
        caption.text = "THE RESEARCHER PREPARES THE SAMPLE"
        shot_position = Vector3(-1.55, 2.45, 4.8)
        shot_target = Vector3(-0.82, 1.45, -0.72)
    elif elapsed < 18.0:
        caption.text = "A SPOONFUL OF YOGURT"
        shot_position = Vector3(0.85, 2.1, 3.6)
        shot_target = Vector3(0.72, 1.18, 0.56)
    elif elapsed < 24.0:
        caption.text = "ANTS APPROACH THE SAMPLE"
        shot_position = Vector3(1.45, 1.85, 2.85)
        shot_target = Vector3(0.72, 1.18, 0.56)
    elif elapsed < 30.0:
        caption.text = "THE EXPERIMENT TAKES A TURN"
        shot_position = Vector3(-1.35, 2.4, 4.65)
        shot_target = Vector3(-0.82, 1.5, -0.72)
    else:
        caption.text = "WHAT WILL THE ANTS DO?"
        shot_position = Vector3(0.0, 2.6, 6.5)
        shot_target = Vector3(0.0, 1.35, 0.0)
    camera.position = camera.position.lerp(shot_position, min(delta * 2.0, 1.0))
    camera.look_at(shot_target, Vector3.UP)
    if character != null:
        character.rotation.y = sin(elapsed * 0.45) * 0.08
    for i in range(ants.size()):
        var phase := elapsed * (0.8 + float(i) * 0.035) + float(i) * TAU / float(ants.size())
        ants[i].position = Vector3(
            0.72 + cos(phase) * (0.27 + float(i % 3) * 0.07),
            1.18 + abs(sin(elapsed * 5.0 + float(i))) * 0.018,
            0.56 + sin(phase) * (0.23 + float(i % 2) * 0.08)
        )
        ants[i].rotation.y = -phase
