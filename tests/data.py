ORDER_CREATED = {
    "@odata.context": "#metadata/Odata.CSC.BatchOrder",
    "value": {
        "Name": "data_download_datahub_order",
        "Priority": 1,
        "WorkflowName": "data-download",
        "NotificationEndpoint": None,
        "NotificationEpUsername": None,
        "NotificationStatus": None,
        "WorkflowOptions": [
            {"Name": "brand", "Value": "staging"},
            {"Name": "platform", "Value": "creodias"},
            {"Name": "version", "Value": "0.0.1"},
            {"Name": "output_storage", "Value": "TEMPORARY"},
            {"Name": "input_catalogue_type", "Value": "STAC"},
            {"Name": "input_catalogue_collection", "Value": "SENTINEL-2"},
            {
                "Name": "input_catalogue_url",
                "Value": "https://datahub.creodias.eu/stac",
            },
        ],
        "Id": 1374977,
        "Status": "queued",
        "SubmissionDate": "2024-02-09T09:58:45.365Z",
        "EstimatedDate": None,
        "KeycloakUUID": "d466132e-2106-4654-8e2e-9bab70f75e2e",
        "WorkflowId": 914,
        "WorkflowDisplayName": "Disp data_download",
        "WorkflowVersion": "0.0.1",
    },
}

ORDER_BODY = {"WorkflowName": "card_bs", "Name": "card_bs_order"}

IDENTIFIERS = [
    "S2A_MSIL1C_20150704T101006_N0204_R022_T31SGR_20150704T101337",
    "S2A_MSIL1C_20150704T101006_N0204_R022_T33UXB_20150704T101337",
    "S2A_MSIL1C_20150704T101006_N0204_R022_T34WET_20150704T101001",
    "S2A_MSIL1C_20150704T101006_N0204_R022_T33UVA_20150704T101337",
    "S2A_MSIL1C_20150704T101006_N0204_R022_T35XNA_20150704T101001",
    "S2A_MSIL1C_20150704T101006_N0204_R022_T31QGE_20150704T102420",
    "S2A_MSIL1C_20150704T101006_N0204_R022_T32UQV_20150704T101337",
]

CATALOGUE_URL = (
    "https://datahub.creodias.eu/odata/v1/Products?$filter=(("
    "ContentDate/Start%20ge%202024-01-01T00:00:00.000Z%20and%20ContentDate/Start%20le%202024-02-07T23:59"
    ":59.999Z)%20and%20(Online%20eq%20true)%20and%20((((("
    "Collection/Name%20eq%20%27SENTINEL-1%27)%20and%20(((Attributes/OData.CSC.StringAttribute/any("
    "i0:i0/Name%20eq%20%27productType%27%20and%20i0/Value%20eq%20%27GRD-COG%27)))))))))&$expand"
    "=Attributes&$expand=Assets&$orderby=ContentDate/Start%20asc&$top=20"
)

STAC_CATALOGUE_URL = (
    "https://datahub.creodias.eu/stac/search?limit=10&collections=SENTINEL-1"
)

COMPLETED_ORDER = {
    "@odata.context": "#metadata/Odata.CSC.BatchOrder",
    "value": {
        "Name": "S2A_MSIL1C_20220607T100601_N0400_R022_T46XES_20220607T121007",
        "Priority": 1,
        "WorkflowName": "sen2cor",
        "NotificationEndpoint": None,
        "NotificationEpUsername": None,
        "NotificationStatus": None,
        "WorkflowOptions": [
            {"Name": "brand", "Value": "staging"},
            {"Name": "platform", "Value": "creodias"},
            {"Name": "version", "Value": "2.10"},
            {"Name": "output_storage", "Value": "PUBLIC"},
        ],
        "Id": 1357372,
        "Status": "completed",
        "SubmissionDate": "2023-10-10T01:17:48.367Z",
        "EstimatedDate": None,
        "KeycloakUUID": "d466132e-2106-4654-8e2e-9bab70f75e2e",
        "WorkflowId": 2,
        "WorkflowDisplayName": "Sentinel-2: BoA reflectance",
        "WorkflowVersion": "2.10",
        "Summary": {
            "status": "completed",
            "processing_order_items_count": 0,
            "downloading_order_items_count": 0,
            "done_order_items_count": 0,
            "already_done_order_items_count": 1,
            "queued_order_items_count": 0,
            "failed_or_cancelled_order_items_count": 0,
            "last_order_item_change_timestamp": "2023-10-10T01:23:15.189Z",
        },
    },
}

QUERY_DETAILS = {
    "parallel_quota": 50,
    "query_url": "https://datahub.creodias.eu/odata/v1/Products?%24filter=%28%28ContentDate%2FStart+ge"
    "+2024-02-06T00%3A00%3A00.000Z+and+ContentDate%2FStart+le+2024-02-07T23%3A59%3A59.999Z"
    "%29+and+%28Online+eq+true%29+and+%28%28%28%28%28Collection%2FName+eq+%27SENTINEL-1%27"
    "%29+and+%28%28%28Attributes%2FOData.CSC.StringAttribute%2Fany%28i0%3Ai0%2FName+eq"
    "+%27productType%27+and+i0%2FValue+eq+%27CARD-BS%27%29%29%29%29%29%29%29%29%29"
    "&%24expand=Attributes&%24expand=Assets&%24orderby=ContentDate%2FStart+asc&%24top=5"
    "&%24count=true",
    "new_orders": False,
}

QUERY_RESPONSE = {
    "@odata.context": "$metadata#Products(Attributes())(Assets())",
    "@odata.count": 18,
    "value": [
        {
            "@odata.mediaContentType": "application/octet-stream",
            "Id": "c30ec00f-5701-4d3b-869b-101a7a57923e",
            "Name": "S1A_IW_GRDH_1SDV_20240206T041137_20240206T041202_052433_06574A_9703_CARD_BS",
            "ContentType": "application/octet-stream",
            "ContentLength": 5159453518,
            "OriginDate": "2024-02-07T01:01:37.569Z",
            "PublicationDate": "2024-02-07T02:22:09.757Z",
            "ModificationDate": "2024-02-07T02:22:39.887Z",
            "Online": True,
            "EvictionDate": "",
            "S3Path": "/eodata/Sentinel-1/SAR/CARD-BS/2024/02/06"
            "/S1A_IW_GRDH_1SDV_20240206T041137_20240206T041202_052433_06574A_9703_CARD_BS",
            "Checksum": [
                {
                    "Value": "5bf9a30a7a03e1421ffad90565001466",
                    "Algorithm": "MD5",
                    "ChecksumDate": "2024-02-07T02:22:34.598296Z",
                },
                {
                    "Value": "8651f31efedd4274e3fc1bd5e17dd328cd60965dd265bb721bdb267b80d9c710",
                    "Algorithm": "BLAKE3",
                    "ChecksumDate": "2024-02-07T02:22:39.764002Z",
                },
            ],
            "ContentDate": {
                "Start": "2024-02-06T04:11:37.189Z",
                "End": "2024-02-06T04:12:02.187Z",
            },
            "Footprint": "geography'SRID=4326;POLYGON ((32.438717 51.678623, 32.944637 53.170662, 29.090103 53.580101, "
            "28.712437 52.085339, 32.438717 51.678623))'",
            "GeoFootprint": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [32.438717, 51.678623],
                        [32.944637, 53.170662],
                        [29.090103, 53.580101],
                        [28.712437, 52.085339],
                        [32.438717, 51.678623],
                    ]
                ],
            },
            "Attributes": [
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "origin",
                    "Value": "CLOUDFERRO",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.IntegerAttribute",
                    "Name": "datatakeID",
                    "Value": 415562,
                    "ValueType": "Integer",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "timeliness",
                    "Value": "NRT-3h",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.IntegerAttribute",
                    "Name": "cycleNumber",
                    "Value": 314,
                    "ValueType": "Integer",
                },
                {
                    "@odata.type": "#OData.CSC.IntegerAttribute",
                    "Name": "orbitNumber",
                    "Value": 52433,
                    "ValueType": "Integer",
                },
                {
                    "@odata.type": "#OData.CSC.IntegerAttribute",
                    "Name": "sliceNumber",
                    "Value": 3,
                    "ValueType": "Integer",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "productClass",
                    "Value": "S",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "processorName",
                    "Value": "CARD_BS",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "orbitDirection",
                    "Value": "DESCENDING",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                    "Name": "processingDate",
                    "Value": "2024-02-07T02:15:21.670000+00:00",
                    "ValueType": "DateTimeOffset",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "operationalMode",
                    "Value": "IW",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "processingLevel",
                    "Value": "LEVEL2",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "swathIdentifier",
                    "Value": "IW",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "processingCenter",
                    "Value": "Production Service-CloudFerro",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "processorVersion",
                    "Value": "3.6.2",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "platformShortName",
                    "Value": "SENTINEL-1",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "instrumentShortName",
                    "Value": "SAR",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.IntegerAttribute",
                    "Name": "relativeOrbitNumber",
                    "Value": 36,
                    "ValueType": "Integer",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "polarisationChannels",
                    "Value": "VV&VH",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "platformSerialIdentifier",
                    "Value": "A",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.DoubleAttribute",
                    "Name": "startTimeFromAscendingNode",
                    "Value": 2086702.0,
                    "ValueType": "Double",
                },
                {
                    "@odata.type": "#OData.CSC.DoubleAttribute",
                    "Name": "completionTimeFromAscendingNode",
                    "Value": 2111700.0,
                    "ValueType": "Double",
                },
                {
                    "@odata.type": "#OData.CSC.StringAttribute",
                    "Name": "productType",
                    "Value": "CARD-BS",
                    "ValueType": "String",
                },
                {
                    "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                    "Name": "beginningDateTime",
                    "Value": "2024-02-06T04:11:37.189Z",
                    "ValueType": "DateTimeOffset",
                },
                {
                    "@odata.type": "#OData.CSC.DateTimeOffsetAttribute",
                    "Name": "endingDateTime",
                    "Value": "2024-02-06T04:12:02.187Z",
                    "ValueType": "DateTimeOffset",
                },
            ],
            "Assets": [],
        }
    ],
    "@odata.nextLink": "https://datahub.creodias.eu/odata/v1/Products?%24filter=%28%28ContentDate"
    "%2FStart+ge+2024-02-06T00%3A00%3A00.000Z+and+ContentDate%2FStart+le+2024-02"
    "-07T23%3A59%3A59.999Z%29+and+%28Online+eq+true%29+and+%28%28%28%28%28Collection"
    "%2FName+eq+%27SENTINEL-1%27%29+and+%28%28%28Attributes%2FOData.CSC"
    ".StringAttribute%2Fany%28i0%3Ai0%2FName+eq+%27productType%27+and+i0%2FValue+eq"
    "+%27CARD-BS%27%29%29%29%29%29%29%29%29%29&%24expand=Attributes&%24expand=Assets"
    "&%24orderby=ContentDate%2FStart+asc&%24top=1&%24count=true&%24skip=1",
}

CATALOGUE_KEYCLOAK_DATA = {
    "client_id": "",
    "username": "",
    "password": "",
    "client_secret": "",
    "keycloak_address": "",
}

ORDERING_KEYCLOAK_DATA = {
    "client_id": "",
    "username": "",
    "password": "",
    "client_secret": "",
    "keycloak_address": "",
    "host": "",
}

KEYCLOAK_RESPONSE = {
    "access_token": "eyFSAJGGa532tdsajgdgdsaakjgk436sgdhjgdsjgdhaj643ygdsdgsagAGDSADGASGAShda&%#&&GSZGDSAGDAGDAGYDSGDAE626esggdsaggdadgdgdagagdasgeayeeyg22",
    "expires_in": 300,
    "refresh_expires_in": 1800,
    "refresh_token": "xbFEAJGGa532tdsajgdgdsaakjgk436sgdhjgdsjgdhaj643ygdsdgsagAGDSADGASGAShda&%#&&GSZGDSAGDAGDAGYDSGDAE626esggdsaggdadgdgdagagdasgeayeas14",
    "token_type": "bearer",
    "not-before-policy": 0,
    "session_state": "cb1c326a-e251-1b25-df46-25e28c0f72zt",
}
