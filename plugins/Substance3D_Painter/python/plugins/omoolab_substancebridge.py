
# Substance 3D Painter modules
import substance_painter.ui
import substance_painter.logging
import substance_painter.project
import substance_painter.export
import substance_painter_plugins
from substance_painter.baking import BakingParameters

from pathlib import Path
import asyncio

from PySide2.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)

from PySide2 import QtWidgets
from configparser import ConfigParser

config = ConfigParser()


class Logger():
    def __init__(self):
        pass

    def info(self, message: str):
        substance_painter.logging.log(
            substance_painter.logging.INFO,
            "SubstanceBridge",
            message
        )

    def error(self, message: str):
        substance_painter.logging.log(
            substance_painter.logging.ERROR,
            "SubstanceBridge",
            message
        )

    def warning(self, message: str):
        substance_painter.logging.log(
            substance_painter.logging.WARNING,
            "SubstanceBridge",
            message
        )


class LabeledInput(QWidget):
    def __init__(self, label, widget: QWidget = QLineEdit()):
        super().__init__()
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)

        self.setLayout(layout)
        self.input = widget


class SubstanceBridgePlugin():
    def __init__(self):

        # Main Tool Bar
        toolbar_layout = QHBoxLayout()

        self.create_project_btn = QPushButton("Create Project")
        self.create_project_btn.clicked.connect(self.on_create_project)
        toolbar_layout.addWidget(self.create_project_btn)

        self.export_btn = QPushButton("Export Textures")
        self.export_btn.clicked.connect(self.on_export)
        self.export_btn.setVisible(False)
        toolbar_layout.addWidget(self.export_btn)

        self.set_mesh_btn = QPushButton("Reload Mesh")
        self.set_mesh_btn.clicked.connect(self.on_set_mesh)
        self.set_mesh_btn.setVisible(False)
        toolbar_layout.addWidget(self.set_mesh_btn)

        self.in_bridge_path = LabeledInput("Bridge Path:")
        toolbar_layout.addWidget(self.in_bridge_path)

        self.set_path_btn = QPushButton("Set Path")
        self.set_path_btn.clicked.connect(self.on_set_path)
        self.set_path_btn.setVisible(False)
        toolbar_layout.addWidget(self.set_path_btn)

        config_btn = QPushButton("Config")
        config_btn.clicked.connect(self.on_config)
        toolbar_layout.addWidget(config_btn)

        self.toolbar_content = QWidget()
        self.toolbar_content.setLayout(toolbar_layout)
        self.toolbar = substance_painter.ui.add_toolbar(
            "Substance Bridge", "sb_toolbar"
        )
        self.toolbar.addWidget(self.toolbar_content)

        # Config Panel
        config_layout = QVBoxLayout()

        alias_layout = QHBoxLayout()
        self.in_alias_or = QLineEdit()
        self.in_alias_as = QLineEdit()
        alias_layout.addWidget(self.in_alias_or)
        alias_layout.addWidget(QLabel("alias as"))
        alias_layout.addWidget(self.in_alias_as)
        self.in_alias_or.textChanged.connect(self.on_set_alias_or)
        self.in_alias_as.textChanged.connect(self.on_set_alias_as)

        alias = QWidget()
        alias.setLayout(alias_layout)
        config_layout.addWidget(QLabel("Bridge Path Alias:"))
        config_layout.addWidget(alias)

        self.config_content = QWidget()
        self.config_content.setLayout(config_layout)
        self.config_content.setWindowTitle("Substance Bridge Config")

        self.config_panel = substance_painter.ui.add_dock_widget(
            self.config_content)
        self.config_panel.show()

        # Other Stuffs
        self.project_data = substance_painter.project.Metadata(
            "SubstanceBridge")
        self.config_path = Path(Path.home(), ".substance_bridge.ini")
        self.log = Logger()

        self.in_alias_or.setText(self.get_config("alias_or") or "")
        self.in_alias_as.setText(self.get_config("alias_as") or "")
        

        substance_painter.event.DISPATCHER.connect(
            substance_painter.event.ProjectEditionLeft,
            self.on_close_project
        )

        substance_painter.event.DISPATCHER.connect(
            substance_painter.event.ProjectEditionEntered,
            self.on_load_project
        )

    @property
    def bridge_path(self):
        bridge_path = self.project_data.get("bridge_path")
        return Path(bridge_path) if bridge_path else None

    @property
    def base_mat(self):
        resources = substance_painter.resource.search("OmooLab_Base")
        if len(resources) == 0:
            self.log.error("Get no base mat!")
            return None
        else:
            return resources[0]

    def on_create_project(self):
        self.log.info("Create project...")


        self.bridge_path_alias_update()
        bridge_path = Path(self.in_bridge_path.input.text())

        if not bridge_path.is_dir():
            self.log.error("No bridge path found!")
            return

        model_name = bridge_path.name
        model_path = Path(bridge_path, f"{model_name}.usd")
        model_high_path = Path(bridge_path, f"{model_name}_High.usd")

        if (not model_path.is_file()) or (not model_high_path.is_file()):
            self.log.error("No model found!")
            return

        textures_path = Path(bridge_path, "Textures")
        user_config_path = Path(substance_painter_plugins.path[0]).parent
        template_path = Path(
            user_config_path, "assets/templates/OmooLab Standard Surface.spt")

        settings = substance_painter.project.Settings(
            default_save_path=None,
            default_texture_resolution=2048,
            export_path=textures_path.as_posix(),
            import_cameras=False,
            mesh_unit_scale=None,
            normal_map_format=substance_painter.project.NormalMapFormat.OpenGL,
            project_workflow=substance_painter.project.ProjectWorkflow.UVTile,
            tangent_space_mode=substance_painter.project.TangentSpace.PerVertex,
            usd_settings=substance_painter.project.UsdSettings(
                scope_name='/',
                variants=None,
                subdivision_level=1,
                frame=0
            )
        )

        if not template_path.is_file():
            self.log.error("No template found!")
            return

        # Close the project currently opened:
        if substance_painter.project.is_open():
            substance_painter.project.close()
            
        substance_painter.project.create(
            mesh_file_path=model_path.as_posix(),
            template_file_path=template_path.as_posix(),
            settings=settings
        )
        
        # Show the current state of the project:
        if substance_painter.project.is_open():
            self.project_data.set("bridge_path", bridge_path.as_posix())
            self.project_data.set("new_project", "1")


    def on_export(self):
        self.log.info("Export textures...")

        if not self.bridge_path:
            self.log.error("No bridge path set!")
            return

        textures_path = Path(self.bridge_path, "Textures")

        if not textures_path.is_dir():
            self.log.error("No texture directory found!")
            return

        export_preset = substance_painter.resource.ResourceID(
            context="your_assets", name="OmooLab Substance Bridge")

        # Set the details of the export (a comprehensive example of all the
        # configuration options is presented at the bottom of the page):
        stack = substance_painter.textureset.get_active_stack()
        export_config = {
            "exportShaderParams": False,
            "exportPath": textures_path.as_posix(),
            "defaultExportPreset": export_preset.url(),
            "exportList": [{"rootPath": str(stack)}],
            "exportParameters": [
                {
                    "parameters": {
                        "dithering": True,
                        "paddingAlgorithm": "infinite"
                    }
                }]
        }

        # Display the list of textures that should be exported, according to the
        # configuration:
        export_list = substance_painter.export.list_project_textures(
            export_config)
        for k, v in export_list.items():
            print("Stack {0}:".format(k))
            for to_export in v:
                print(to_export)

        substance_painter.export.export_project_textures(export_config)

    def on_set_alias_or(self):
        self.set_config("alias_or", self.in_alias_or.text())

    def on_set_alias_as(self):
        self.set_config("alias_as", self.in_alias_as.text())

    def on_set_path(self):
        self.log.info("Set path...")
        self.bridge_path_alias_update()
        bridge_path = Path(self.in_bridge_path.input.text())
        self.project_data.set("bridge_path", bridge_path.as_posix())

        self.on_set_mesh()

    def on_set_mesh(self):
        self.log.info("Set mesh...")

        if not self.bridge_path:
            self.log.error("No bridge path set!")
            return

        model_name = self.bridge_path.name
        model_path = Path(self.bridge_path, f"{model_name}.usd")

        if not model_path.is_file():
            self.log.error("No model found!")
            return

        settings = substance_painter.project.MeshReloadingSettings(
            import_cameras=False,
            preserve_strokes=True
        )

        if substance_painter.project.is_open():
            self.project_data.set("new_mesh", "1")
            
        # Function that will be called when reloading is finished:
        def on_mesh_reload(status: substance_painter.project.ReloadMeshStatus):
            if status == substance_painter.project.ReloadMeshStatus.SUCCESS:
                print("The mesh reimported successfully.")
            else:
                print("The mesh couldn't be reloaded.")

        # Reload the current mesh:
        substance_painter.project.reload_mesh(
            mesh_file_path=model_path.as_posix(),
            settings=settings,
            loading_status_cb=on_mesh_reload
        )

    def on_config(self):
        self.config_panel.show()

    def on_load_project(self, e=None):
        self.log.info("Load project...")
        self.create_project_btn.setVisible(False)
        self.set_path_btn.setVisible(True)
        self.set_mesh_btn.setVisible(True)
        self.export_btn.setVisible(True)

        if not self.bridge_path:
            self.log.info("No bridge path set, do nothing")
            return
        
        self.in_bridge_path.input.setText(str(self.bridge_path))
        
        if self.project_data.get("new_mesh") == "1" or self.project_data.get("new_project") == "1":
            
            self.to_baker()
            if self.base_mat:
                self.base_mat.show_in_ui()
            
            self.project_data.set("new_mesh", "0")
            self.project_data.set("new_project", "0")
            

    def on_close_project(self, e=None):
        self.log.info("Close project...")
        self.in_bridge_path.input.setText("")
        self.in_bridge_path.input.setEnabled(True)
        self.create_project_btn.setVisible(True)
        self.set_path_btn.setVisible(False)
        self.set_mesh_btn.setVisible(False)
        self.export_btn.setVisible(False)

    def bridge_path_alias_update(self):
        alias_or = self.in_alias_or.text()
        alias_as = self.in_alias_as.text()
        if alias_or:
            bridge_path = self.in_bridge_path.input.text().replace(alias_or, alias_as)
            self.in_bridge_path.input.setText(bridge_path)

    def set_config(self, key: str, value):
        if not self.config_path.is_file():
            with self.config_path.open("w", encoding="utf-8") as f:
                pass

        config.read(self.config_path, encoding="utf-8")

        if 'Common' not in config:
            config['Common'] = {}

        config['Common'][key] = str(value)

        with self.config_path.open("w", encoding="utf-8") as f:
            config.write(f)

    def get_config(self, key: str):
        if not self.config_path.is_file():
            with self.config_path.open("w", encoding="utf-8") as f:
                pass

        config.read(self.config_path, encoding="utf-8")

        try:
            return config['Common'][key]
        except:
            return None

    def to_baker(self):
        substance_painter.ui.switch_to_mode(
                substance_painter.ui.UIMode.Baking)
        
        self.log.info("Set baking params...")

        if not self.bridge_path:
            self.log.error("No bridge path set!")
            return

        model_name = self.bridge_path.name
        model_high_path = Path(self.bridge_path, f"{model_name}_High.usd")

        if not model_high_path.is_file():
            self.log.error("No model found!")
            return

        texture_sets = substance_painter.textureset.all_texture_sets()
        baking_params = BakingParameters.from_texture_set(texture_sets[0])
        common_params = baking_params.common()
        BakingParameters.set({
            common_params['HipolyMesh']: f"file:///{model_high_path.as_posix()}",
            # common_params['FilterMethod']: common_params['FilterMethod'].enum_value('By Mesh Name')
        })

    def __del__(self):
        substance_painter.ui.delete_ui_element(self.toolbar)
        substance_painter.ui.delete_ui_element(self.config_panel)


SUBSTANCE_BRIDGE = None


def start_plugin():
    global SUBSTANCE_BRIDGE
    SUBSTANCE_BRIDGE = SubstanceBridgePlugin()


def close_plugin():
    global SUBSTANCE_BRIDGE
    del SUBSTANCE_BRIDGE


if __name__ == "__main__":
    start_plugin()
