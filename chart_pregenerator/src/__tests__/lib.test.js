import 'node-fetch';
import { generateBarChartSVG, generateTreemapChartSVG, generateUSMapSVG } from '../lib'

const test_csv = `date,assailant,tags,categories
2023-07-15,,"platypus, storks, tarsier","Arrest / Criminal Charge, Border Stop, Leak Case"
2023-07-13,politician,"squids, storks, tarsier","Assault, Border Stop, Leak Case"
2023-07-13,private individual,"mongoose, opossom, oysters","Assault, Equipment Damage, Equipment Search or Seizure"
2023-07-13,,"ants, mongoose, tortoises","Chilling Statement, Equipment Damage, Other Incident"
2023-07-12,,"hummingbirds, hyena, stick insects","Border Stop, Equipment Damage, Other Incident"
2023-07-11,,"mongoose, wombat","Equipment Damage, Equipment Search or Seizure"
2023-07-11,unknown,"dragonflies, echidna, squids","Arrest / Criminal Charge, Assault, Other Incident"
2023-07-11,,"opossom, seaweed, snakes","Chilling Statement, Denial of Access, Equipment Search or Seizure"
2023-07-10,,"dragonflies, plum, rodents","Other Incident, Prior Restraint, Subpoena / Legal Order"
2023-07-10,law enforcement,"echidna, mantises, octopuses","Arrest / Criminal Charge, Assault, Other Incident"
2023-07-09,,"chrysanthemum, flowers, opossom","Denial of Access, Equipment Search or Seizure, Subpoena / Legal Order"
2023-07-08,,flamingoes,Border Stop
2023-07-07,,"bamboo, echidna","Arrest / Criminal Charge, Subpoena / Legal Order"
2023-07-07,private security,"octopuses, platypus","Arrest / Criminal Charge, Assault"
2023-07-07,law enforcement,"ammonites, hyena, platypus","Arrest / Criminal Charge, Assault, Equipment Damage"
2023-07-07,,"Important Animals, kangaroo, mongoose, rabbits","Equipment Damage, Equipment Search or Seizure, Prior Restraint"
2023-07-06,,"aphids, shrews, tarsier","Leak Case, Other Incident, Prior Restraint"
2023-07-05,,"civet, flamingoes","Border Stop, Equipment Damage"
2023-07-04,unknown,"octopuses, orchid, tarsier","Assault, Leak Case, Subpoena / Legal Order"`;

const test_categories = `[
    {
        "id": 4,
        "title": "Arrest / Criminal Charge",
        "methodology": "Unit community before environmental another book. Blue inside candidate admit scene popular here. Course evening determine hand attorney about. Maybe avoid half. Family structure occur need might position.",
        "plural_name": "Arrests and Criminal Charges",
        "slug": "arrest-criminal-charge",
        "url": "http://localhost:8000/arrest-criminal-charge/"
    },
    {
        "id": 5,
        "title": "Border Stop",
        "methodology": "Star positive situation clearly as. Couple fire eight two condition right. Fact budget position appear. Decision clearly stop center could. Year turn summer improve door. Kitchen whom here question treatment clear question.",
        "plural_name": "Border Stops",
        "slug": "border-stop",
        "url": "http://localhost:8000/border-stop/"
    },
    {
        "id": 6,
        "title": "Denial of Access",
        "methodology": "Data company minute population. Remain idea quality rather why customer the. High step daughter maintain forget community scientist. Quality rise structure partner several hospital.",
        "plural_name": "Denials of Access",
        "slug": "denial-access",
        "url": "http://localhost:8000/denial-access/"
    }
]`;

jest.mock('node-fetch', () => jest.fn((path) => Promise.resolve({ text: () => {
	if (path === "http://app:8000/api/edge/categories/")
		return Promise.resolve(test_categories)
	return Promise.resolve(test_csv)
}})));

test('renders Bar Chart with dummy data', async () => {
	expect(await generateBarChartSVG()).toMatchSnapshot()
})

test('renders Stacked Bar Chart with dummy data', async () => {
	expect(await generateBarChartSVG({ query: {
		options: JSON.stringify({"branchFieldName":"assailant","branches":{"type":"list","value":[{"title":"unknown","value":"UNKNOWN"},{"title":"law enforcement","value":"LAW_ENFORCEMENT"},{"title":"private security","value":"PRIVATE_SECURITY"},{"title":"politician","value":"POLITICIAN"},{"title":"public figure","value":"PUBLIC_FIGURE"},{"title":"private individual","value":"PRIVATE_INDIVIDUAL"}]}})
	}})).toMatchSnapshot()
})

test('renders Treemap Chart with dummy data', async () => {
	expect(await generateTreemapChartSVG()).toMatchSnapshot()
})

test('renders grouped Treemap Chart with dummy data', async () => {
	expect(await generateTreemapChartSVG({ query: {
			options: JSON.stringify({"branchFieldName":"assailant","branches":{"type":"list","value":[{"title":"unknown","value":"UNKNOWN"},{"title":"law enforcement","value":"LAW_ENFORCEMENT"},{"title":"private security","value":"PRIVATE_SECURITY"},{"title":"politician","value":"POLITICIAN"},{"title":"public figure","value":"PUBLIC_FIGURE"},{"title":"private individual","value":"PRIVATE_INDIVIDUAL"}]}})
		}})).toMatchSnapshot()
})

test('renders Bubble Map with dummy data', async () => {
	expect(await generateUSMapSVG()).toMatchSnapshot()
})
