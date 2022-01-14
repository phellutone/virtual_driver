
import enum
from typing import Union
import bpy
from .utils import Interpretation, animatable

class FCurveObserverState(enum.Enum):
    INPUT_ID = 'INPUT_ID'
    INPUT_DATA_PATH = 'INPUT_DATA_PATH'
    INPUT_ARRAY_INDEX = 'INPUT_ARRAY_INDEX'
    ANIMATION_DATA = 'ANIMATION_DATA'
    DATA_PATH = 'DATA_PATH'
    ARRAY_INDEX = 'ARRAY_INDEX'
    VALID_DUPLICATE = 'VALID_DUPLICATE'
    VALID_ONE = 'VALID_ONE'

class FCurveObserver(bpy.types.PropertyGroup):
    def fcurve_update(self, context: bpy.types.Context) -> None:
        fcurves = get(self.id_data, self.path_from_id('prop'), 0)
        if fcurves is None:
            if self.fcurve:
                # no fcurve and prop is true so set prop to false, recursive called but nothig do
                self.fcurve = False
        else:
            if not self.fcurve:
                # exist fcurve and prop is false so delete fcurve
                delete(self.id_data, self.path_from_id('prop'), 0)

    fcurve: bpy.props.BoolProperty(
        update=fcurve_update
    )

    id: bpy.props.PointerProperty(type=bpy.types.ID)
    data_path: bpy.props.StringProperty()
    prop: bpy.props.FloatProperty()

def parser_for_fcurve(anim: Interpretation) -> Union[tuple[bpy.types.ID, str, int], None]:
    if anim is None:
        return
    return (
        anim.id,
        (anim.id.path_resolve(anim.rna_path) if anim.rna_path else anim.id).path_from_id(anim.prop_path),
        0 if anim.array_index is None else anim.array_index
    )

def get(id: bpy.types.ID, data_path: str, array_index: int) -> Union[bpy.types.FCurve, list[bpy.types.FCurve], None]:
    state = observer(id, data_path, array_index)
    if state in (FCurveObserverState.VALID_ONE, FCurveObserverState.VALID_DUPLICATE):
        anim_data: bpy.types.AnimData = getattr(id, 'animation_data')
        fcurves: list[bpy.types.FCurve] = anim_data.drivers
        fcurves = [f for f in fcurves if f.data_path == data_path and f.array_index == array_index]
        return fcurves[0] if state is FCurveObserverState.VALID_ONE else fcurves
    if state in (FCurveObserverState.INPUT_ID, FCurveObserverState.INPUT_DATA_PATH, FCurveObserverState.INPUT_ARRAY_INDEX):
        return
    if state in (FCurveObserverState.ANIMATION_DATA, ):
        return
    if state in (FCurveObserverState.DATA_PATH, FCurveObserverState.ARRAY_INDEX):
        return

def delete(id: bpy.types.ID, data_path: str, array_index: int) -> None:
    state = observer(id, data_path, array_index)
    if state in (FCurveObserverState.VALID_ONE, FCurveObserverState.VALID_DUPLICATE):
        anim_data: bpy.types.AnimData = getattr(id, 'animation_data')
        fcurves: list[bpy.types.FCurve] = anim_data.drivers
        fcurves = [f for f in fcurves if f.data_path == data_path and f.array_index == array_index]
        for fcurve in fcurves:
            anim_data_drivers: bpy.types.AnimDataDrivers = anim_data.drivers
            anim_data_drivers.remove(fcurve)
        return
    if state in (FCurveObserverState.INPUT_ID, FCurveObserverState.INPUT_DATA_PATH, FCurveObserverState.INPUT_ARRAY_INDEX):
        return
    if state in (FCurveObserverState.ANIMATION_DATA, ):
        return
    if state in (FCurveObserverState.DATA_PATH, FCurveObserverState.ARRAY_INDEX):
        return

def observer(id: bpy.types.ID, data_path: str, array_index: int) -> FCurveObserverState:
    if not isinstance(id, bpy.types.ID) or not hasattr(id, 'animation_data'):
        return FCurveObserverState.INPUT_ID
    if not isinstance(data_path, str) or data_path == '':
        return FCurveObserverState.INPUT_DATA_PATH
    if not isinstance(array_index, int) or array_index < 0:
        return FCurveObserverState.INPUT_ARRAY_INDEX
    anim_data: Union[bpy.types.AnimData, None] = getattr(id, 'animation_data', None)
    if anim_data is None:
        return FCurveObserverState.ANIMATION_DATA
    fcurves: list[bpy.types.FCurve] = anim_data.drivers
    pfcurves = [f for f in fcurves if f.data_path == data_path]
    if not pfcurves:
        return FCurveObserverState.DATA_PATH
    ifcurves = [f for f in pfcurves if f.array_index == array_index]
    if not ifcurves:
        return FCurveObserverState.ARRAY_INDEX
    if len(ifcurves) > 1:
        return FCurveObserverState.VALID_DUPLICATE
    return FCurveObserverState.VALID_ONE