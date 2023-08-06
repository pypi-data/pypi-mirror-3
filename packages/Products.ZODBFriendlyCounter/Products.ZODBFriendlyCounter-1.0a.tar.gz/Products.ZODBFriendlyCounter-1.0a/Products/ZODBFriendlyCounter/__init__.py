import ZFC

def initialize(context):
    "Initialize the product"
    context.registerClass(
        ZFC.ZFC,
        constructors = (
            ZFC.manage_add_zfc,
            ZFC.manage_add_zfc,
        )
    )

